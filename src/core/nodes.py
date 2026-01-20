import time
from datetime import datetime
from typing import Literal

from langchain_core.messages import SystemMessage, ToolMessage

# IMPORTS PROPIOS
from src.core.llm_client import get_chat_model
from src.core.prompts import MONDRI_IDENTITY
from src.core.state import AgentState

# Importamos las skills para vincularlas y crear el mapa
from src.skills import ALL_SKILLS

# [NUEVO] Mapeo dinámico: Nombre de la herramienta -> Función real
# Esto evita tener que escribir "if tool == 'nombre'" manualmente.
TOOL_MAP = {t.name: t for t in ALL_SKILLS}


# --- NODO AGENTE ---
def agent_node(state: AgentState):
    # ESTRATEGIA: Usamos Groq (Llama 3.3) para velocidad extrema
    llm = get_chat_model(
        temperature=0.7, provider="groq", model_name="llama-3.3-70b-versatile"
    )

    # El Agente NO tiene tools vinculadas, solo charla.

    current_time = datetime.now().strftime("%A %d de %B de %Y, %H:%M")
    time_context = f"\n[System Time: {current_time}]\n"
    full_system_prompt = MONDRI_IDENTITY + time_context

    system_msg = SystemMessage(content=full_system_prompt)
    messages = [system_msg] + state["messages"]

    start_time = time.time()
    try:
        # Invocamos directo
        response = llm.invoke(messages)

        duration = time.time() - start_time
        log_msg = f"💬 [Agent] Mondri (Groq) respondió en {duration:.2f}s"

        return {"messages": [response], "debug_logs": [log_msg]}
    except Exception as e:
        return {"messages": [], "debug_logs": [f"⚠️ Error en Agent: {e}"]}


# --- NODO HERRAMIENTAS (CORREGIDO) ---
def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls:
        return {"messages": []}

    results = []
    logs = []

    for call in tool_calls:
        tool_name = call["name"]
        tool_args = call["args"]  # Gemini ya nos da esto como diccionario limpio

        start_tool = time.time()

        # BUSCAMOS LA HERRAMIENTA EN EL MAPA
        if tool_name in TOOL_MAP:
            try:
                # [CORRECCIÓN CRÍTICA]
                # Pasamos 'tool_args' DIRECTAMENTE a la herramienta.
                # Ya no intentamos buscar "text" ni convertir a string.
                tool_instance = TOOL_MAP[tool_name]
                output = tool_instance.invoke(tool_args)
            except Exception as e:
                output = f"Error crítico ejecutando skill {tool_name}: {str(e)}"
        else:
            output = f"Error: Skill '{tool_name}' no encontrada en TOOL_MAP. Revisa src/skills/__init__.py"

        duration = time.time() - start_tool

        # Log para UI
        logs.append(f"🛠️ [Tool] {tool_name} ejecutada en {duration:.2f}s")

        results.append(
            ToolMessage(tool_call_id=call["id"], name=tool_name, content=str(output))
        )

    return {"messages": results, "debug_logs": logs}


# --- LOGICA CONDICIONAL ---
def should_continue(state: AgentState) -> Literal["tools", "agent"]:
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])
    if tool_calls:
        return "tools"
    return "agent"
