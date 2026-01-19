import os
from datetime import datetime
from typing import Literal

from langchain_core.messages import SystemMessage, ToolMessage

# IMPORTS PROPIOS
from src.core.llm_client import get_chat_model
from src.core.prompts import MONDRI_IDENTITY
from src.core.state import AgentState
from src.skills import (
    ALL_SKILLS,
    get_user_profile,
    process_expense,
    save_thought,
    save_todo,
    update_user_profile,
)


# --- NODO AGENTE ---
def agent_node(state: AgentState):
    # ESTRATEGIA: Personalidad "Uncensored" / Sarcástica
    # Usamos Grok 4.1 Fast de xAI.
    llm = get_chat_model(temperature=0.7, provider="grok", model_name="grok-4-1-fast")

    # Mantenemos las tools en el agente por redundancia
    llm_with_skills = llm.bind_tools(ALL_SKILLS)

    current_time = datetime.now().strftime("%A %d de %B de %Y, %H:%M")
    time_context = f"\n[System Time: {current_time}]\n"

    full_system_prompt = MONDRI_IDENTITY + time_context

    system_msg = SystemMessage(content=full_system_prompt)
    messages = [system_msg] + state["messages"]

    response = llm_with_skills.invoke(messages)
    return {"messages": [response]}


# --- NODO HERRAMIENTAS ---
def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls:
        return {"messages": []}

    results = []
    for call in tool_calls:
        tool_name = call["name"]
        tool_args = call["args"]

        try:
            if tool_name == "process_expense":
                arg = (
                    tool_args.get("text")
                    if isinstance(tool_args, dict) and "text" in tool_args
                    else str(tool_args)
                )
                output = process_expense.invoke(arg)
            elif tool_name == "save_thought":
                output = save_thought.invoke(tool_args)
            elif tool_name == "save_todo":
                output = save_todo.invoke(tool_args)
            elif tool_name == "update_user_profile":
                output = update_user_profile.invoke(tool_args)
            elif tool_name == "get_user_profile":
                output = get_user_profile.invoke(tool_args)
            else:
                output = f"Error: Skill '{tool_name}' no instalada."
        except Exception as e:
            output = f"Error crítico ejecutando skill: {str(e)}"

        results.append(
            ToolMessage(tool_call_id=call["id"], name=tool_name, content=str(output))
        )

    return {"messages": results}


# --- LOGICA CONDICIONAL ---
def should_continue(state: AgentState) -> Literal["tools", "agent"]:
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])
    if tool_calls:
        return "tools"
    return "agent"
