import threading  # Para la memoria en segundo plano
import time
from datetime import datetime

from langchain_core.messages import SystemMessage

# Imports internos
from src.core.llm_client import get_chat_model

# Importamos la Memoria
from src.core.memory import add_memory, get_memories
from src.core.prompts import MONDRI_IDENTITY
from src.core.router import classify_intent
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


# --- 2. NODO FINANZAS (El que te faltaba) ---
def finance_node(state: AgentState):
    """Extrae y guarda gastos."""
    last_msg = state["messages"][-1].content
    start = time.perf_counter()

    result = extract_and_save_expense(last_msg)
    elapsed = time.perf_counter() - start

    if result["status"] == "success":
        report = f"[SYSTEM]: Gasto guardado. Detalles: {result['summary']}. Confirma sarcásticamente."
        log = f"💰 [Finance] Éxito ({elapsed:.2f}s)"
    else:
        report = f"[SYSTEM]: Error guardando gasto: {result['summary']}."
        log = f"❌ [Finance] Error ({elapsed:.2f}s)"

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
        log = f"📅 [Tasks] Éxito ({elapsed:.2f}s)"
    else:
        report = f"[SYSTEM]: Error agendando: {result['summary']}."
        log = f"❌ [Tasks] Error ({elapsed:.2f}s)"

    return {"messages": [SystemMessage(content=report)], "debug_logs": [log]}


# --- 4. NODO AGENTE (ASÍNCRONO / RÁPIDO) ---
def agent_node(state: AgentState):
    """Mondri responde rápido y guarda memoria en segundo plano."""
    # Usamos el modelo grande (70b) o rápido (8b) según prefieras
    llm = get_chat_model(temperature=0.7, model_name="llama-3.3-70b-versatile")

    last_msg = state["messages"][-1].content
    user_id = "andy_dev"

    # A. LECTURA SÍNCRONA (Necesitamos saber esto YA para responder bien)
    memories = get_memories(user_id=user_id, query=last_msg)

    memory_context = ""
    if memories:
        memory_list = "\n- ".join(memories)
        memory_context = f"\n[MEMORIA PREVIA]:\n{memory_list}\n(Úsalo para contexto, no repitas como robot)."
        # Log ligero para consola
        print(f"🧠 [Agent] Hits de memoria: {len(memories)}")

    # B. ESCRITURA ASÍNCRONA (Fire & Forget)
    # Si es información de perfil, guardamos en un hilo aparte para no bloquear el chat.
    intent = state.get("intent")
    if intent == "profile":
        print("🚀 [Background] Guardando memoria en segundo plano...")
        # Creamos y lanzamos el hilo
        threading.Thread(target=add_memory, args=(user_id, last_msg)).start()

    # C. GENERACIÓN DE RESPUESTA
    current_time = datetime.now().strftime("%A %d de %B, %H:%M")
    system_prompt = (
        MONDRI_IDENTITY + f"\n[System Time: {current_time}]" + memory_context
    )

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    try:
        response = llm.invoke(messages)
        return {
            "messages": [response],
            "debug_logs": [f"🧠 Memory Hits: {len(memories)}"],
        }
    except Exception as e:
        return {"messages": [], "debug_logs": [f"⚠️ Error Mondri: {e}"]}
