import threading  # Para la memoria en segundo plano
import time
from datetime import datetime
import re

from langchain_core.messages import SystemMessage, HumanMessage

# Imports internos
from src.core.llm_client import get_chat_model

# Importamos la Memoria
from src.core.memory import add_memory, get_memories
from src.core.prompts import MONDRI_IDENTITY
from src.core.llm_router import classify_intent
from src.core.state import AgentState

# Importamos las Skills (Tus manos)
from src.skills.finance_extractor import extract_and_save_expense
from src.skills.tasks_extractor import extract_and_save_task


# --- 1. NODO ROUTER ---
def router_node(state: AgentState):
    """Clasifica la intención del usuario."""
    last_msg = state["messages"][-1].content
    intent = classify_intent(last_msg)
    return {"intent": intent}


# --- 2. NODO FINANZAS ---
def finance_node(state: AgentState):
    """Extrae y guarda gastos."""
    last_msg = state["messages"][-1].content
    start = time.perf_counter()

    result = extract_and_save_expense(last_msg)
    elapsed = time.perf_counter() - start

    if result["status"] == "success":
        report = f"[SYSTEM]: Gasto guardado. Detalles: {result['summary']}. Confirma sarcásticamente."
        log = f"[FINANCE] Exito ({elapsed:.2f}s)"
    else:
        report = f"[SYSTEM]: Error guardando gasto: {result['summary']}."
        log = f"[ERROR] Finance ({elapsed:.2f}s)"

    return {"messages": [SystemMessage(content=report)], "debug_logs": [log]}


# --- 3. NODO TAREAS ---
def tasks_node(state: AgentState):
    """Extrae y guarda tareas/recordatorios."""
    last_msg = state["messages"][-1].content
    start = time.perf_counter()

    result = extract_and_save_task(last_msg)
    elapsed = time.perf_counter() - start

    if result["status"] == "success":
        report = f"[SYSTEM]: Tarea agendada. Detalles: {result['summary']}. Confirma sarcásticamente que se lo recordarás."
        log = f"[TASKS] Exito ({elapsed:.2f}s)"
    else:
        report = f"[SYSTEM]: Error agendando: {result['summary']}."
        log = f"[ERROR] Tasks ({elapsed:.2f}s)"

    return {"messages": [SystemMessage(content=report)], "debug_logs": [log]}


# --- 4. NODO AGENTE (MEMORIA CONDICIONAL - v3.1) ---
def agent_node(state: AgentState):
    """
    Mondri con memoria CONDICIONAL según el tipo de intención.
    
    FLUJOS:
    - finance/tasks → SKIP memoria (solo confirmar guardado)
    - chat/None → CON memoria (daily.md + Qdrant)
    - profile → ESCRIBE memoria (Qdrant async)
    """
    llm = get_chat_model(temperature=0.7, model_name="llama-3.3-70b-versatile")
    
    last_msg = state["messages"][-1].content
    user_id = "andy_dev"
    intent = state.get("intent")
    
    # --- DECISIÓN CRÍTICA: ¿NECESITA MEMORIA? ---
    memory_context = ""
    memory_mode = "SKIP"
    
    if intent in ["finance", "tasks"]:
        # 🔵 FLUJO RÁPIDO: Sin memoria (solo confirma acción)
        print("[AGENT] FAST PATH: Sin memoria Qdrant")
        memory_mode = "FAST"
        # No leemos Qdrant ni archivos diarios
        
    else:
        # 🟣 FLUJO CONTEXTUAL: Con memoria completa
        print("[AGENT] CONTEXT PATH: Con memoria completa")
        memory_mode = "CONTEXTUAL"
        
        # Importar aquí para evitar import circular
        from src.skills.daily_context import read_daily_context
        
        # 1. Contexto inmediato (archivo de hoy - RÁPIDO ~5ms)
        daily = read_daily_context(max_entries=15)  # Últimas 15 interacciones
        
        # 2. Contexto largo plazo (Qdrant - LENTO ~200-500ms)
        # Solo buscar si la consulta parece necesitar contexto histórico
        memories = []
        if _needs_long_term_memory(last_msg):
            print("[AGENT] Consultando Qdrant...")
            memories = get_memories(user_id=user_id, query=last_msg)
        else:
            print("[AGENT] Sin necesidad de Qdrant")
        
        # Construir contexto compuesto
        memory_parts = []
        if daily:
            memory_parts.append(f"[CONTEXTO INMEDIATO - HOY]:\n{daily}")
        if memories:
            mem_list = "\n- ".join(memories)
            memory_parts.append(f"[SABIDURÍA - MEMORIA LARGO PLAZO]:\n{mem_list}")
        
        if memory_parts:
            memory_context = "\n\n".join(memory_parts)
    
    # --- GENERACIÓN DE RESPUESTA ---
    current_time = datetime.now().strftime("%A %d de %B, %H:%M")
    system_prompt = MONDRI_IDENTITY + f"\n[System Time: {current_time}]"
    
    if memory_context:
        system_prompt += f"\n\n{memory_context}"
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    try:
        response = llm.invoke(messages)
        
        # --- POST-PROCESAMIENTO: GUARDAR CONTEXTO ---
        # Importar aquí para evitar import circular
        from src.skills.daily_context import append_to_daily
        
        # Extraer mensaje REAL del usuario (no system messages)
        user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
        actual_user_msg = user_messages[-1].content if user_messages else last_msg
        
        # SIEMPRE guardar en daily_context (filtrado interno decide si vale la pena)
        append_to_daily(
            user_msg=actual_user_msg,  # ✅ Mensaje real del usuario
            bot_msg=response.content,
            intent=intent
        )
        
        # Guardar en Qdrant de forma inteligente (no solo profile)
        if _should_save_to_longterm(actual_user_msg, intent):
            print(f"[ASYNC] Guardando en Qdrant (intent: {intent or 'permanente'})...")
            threading.Thread(target=add_memory, args=(user_id, actual_user_msg)).start()
        
        return {
            "messages": [response],
            "debug_logs": [f"[AGENT] Memory Mode: {memory_mode}"],
        }
    except Exception as e:
        return {"messages": [], "debug_logs": [f"[ERROR] Mondri: {e}"]}


def _should_save_to_longterm(msg: str, intent: str) -> bool:
    """Detecta si un mensaje contiene información permanente para Qdrant."""
    if intent == "profile":
        return True
    
    # Patrones de datos permanentes
    permanent_patterns = [
        r"me llamo \w+",
        r"soy (de|un|una|del?) \w+",
        r"(me gusta|odio|me encanta|detesto|amo)",
        r"mi \w+ (se llama|es|tiene)",
        r"(alérgico|vegetariano|vegano|celíaco)",
        r"mi sueño es",
        r"siempre (he|quiero|prefiero)",
        r"nunca (como|hago|voy)",
        r"mi (familia|madre|padre|herman)",
        # Nuevos patrones para intereses y aprendizaje
        r"(estoy aprendiendo|estoy estudiando|estoy mejorando)",
        r"(me está gustando|me interesa mucho)",
        r"(ahora (uso|trabajo|programo) (en|con))",
        r"(mi lenguaje favorito|mi framework favorito)",
        r"(trabajo (como|en)|soy (desarrollador|programador|ingeniero))",
    ]
    
    return any(re.search(p, msg.lower()) for p in permanent_patterns)


def _needs_long_term_memory(query: str) -> bool:
    """
    Decide si una consulta necesita contexto de Qdrant (largo plazo).
    
    SÍ necesita si:
    - Pregunta sobre patrones históricos ("gasto mucho", "siempre")
    - Preguntas de perfil ("sabes mi", "qué me gusta")
    - Análisis de tendencias
    
    NO necesita si:
    - Preguntas generales ("qué es X", "cómo funciona Y")
    - Conversación casual
    """
    query_lower = query.lower()
    
    # Patrones que SÍ necesitan contexto histórico
    longterm_patterns = [
        "gasto", "gastado", "cuánto", "siempre", "normalmente",
        "mi nombre", "sabes", "recuerdas", "conoces sobre mí",
        "me gusta", "prefiero", "odio", "alérgico",
        "tendencia", "patrón", "historial", "resumen"
    ]
    
    return any(pattern in query_lower for pattern in longterm_patterns)

