import json
import os
from datetime import datetime
from typing import Annotated, Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from src.core.database import SessionLocal, TransactionModel, init_db

# --- IMPORTS DE TUS MÓDULOS ---
from src.core.prompts import MOON_SYS_PROMPT
from src.modules.finance.service import FinanceService
from src.modules.knowledge.schemas import NoteEntry, TaskEntry
from src.modules.knowledge.service import KnowledgeService

load_dotenv()

# Inicializamos la DB al arrancar
init_db()


# --- 1. Estado ---
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# --- 2. Tools (Las Manos de Moon) ---


@tool
def process_expense(text: str):
    """
    Use this tool ONLY when the user mentions spending money, buying something, or a financial transaction.
    Input: The raw text of the expense.
    """
    print(f"[INFO] Tool 'process_expense' triggered: {text}")
    service = FinanceService()

    try:
        data = service.extract_transaction_data(text)

        db = SessionLocal()
        new_tx = TransactionModel(
            date=data.date,
            amount=data.amount,
            currency=data.currency,
            category=data.category,
            merchant=data.merchant,
            notes=data.notes,
        )
        db.add(new_tx)
        db.commit()
        db.refresh(new_tx)
        db.close()

        return f"Gasto registrado: {data.model_dump_json()}"

    except Exception as e:
        return f"Error processing expense: {str(e)}"


@tool
def save_thought(content: str, tags: str = "", category: str = "general"):
    """
    Use this tool to save generic thoughts, ideas, references, or static information.
    NOT for tasks or things to do later.
    Args:
        content: The main text of the note.
        tags: Comma-separated keywords (e.g. "ideas, projects").
        category: General category (default: 'general').
    """
    print(f"[INFO] Tool 'save_thought' triggered: {content}")

    try:
        db = SessionLocal()
        service = KnowledgeService(db)

        # Convertimos string de tags a lista para el Pydantic Schema
        tag_list = [t.strip() for t in tags.split(",")] if tags else []

        note_data = NoteEntry(content=content, tags=tag_list, category=category)
        result = service.save_note(note_data)
        db.close()

        return json.dumps(result)
    except Exception as e:
        return f"Error saving note: {str(e)}"


@tool
def save_todo(content: str, due_date: Optional[str] = None, priority: str = "normal"):
    """
    Use this tool to save TASKS, reminders, or actions that need to be done in the future.
    Args:
        content: The action to perform (e.g., "Buy milk").
        due_date: ISO 8601 date string or None.
        priority: 'normal', 'high', or 'low'.
    """
    print(f"[INFO] Tool 'save_todo' triggered: {content} | Due: {due_date}")

    try:
        db = SessionLocal()
        service = KnowledgeService(db)

        task_data = TaskEntry(content=content, due_date=due_date, priority=priority)
        result = service.save_task(task_data)
        db.close()

        return json.dumps(result)
    except Exception as e:
        return f"Error saving task: {str(e)}"


# --- 3. Nodos ---


def agent_node(state: AgentState):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.6,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    # Bind de TODAS las herramientas disponibles
    tools = [process_expense, save_thought, save_todo]
    llm_with_tools = llm.bind_tools(tools)

    # --- INYECCIÓN DE TIEMPO REAL ---
    # Esto le da a Moon la capacidad de saber qué día es hoy para calcular "mañana" o "el martes"
    current_time = datetime.now().strftime("%A %d de %B de %Y, %H:%M")

    time_context = (
        f"\n\n[SYSTEM METADATA]\n"
        f"Current System Time: {current_time}\n"
        f"Location: Peru (UTC-5).\n"
        f"If the user says 'tomorrow' or 'next friday', calculate the exact ISO date based on the Current System Time."
    )

    # Concatenamos la personalidad original + el contexto temporal
    full_system_prompt = MOON_SYS_PROMPT + time_context

    system_msg = SystemMessage(content=full_system_prompt)
    messages = [system_msg] + state["messages"]

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return {"messages": []}

    results = []
    for call in last_message.tool_calls:
        tool_name = call["name"]
        tool_args = call["args"]

        # Router manual de herramientas
        if tool_name == "process_expense":
            # Nota: process_expense espera un string directo 'text'
            # pero a veces el LLM manda un dict. Manejamos ambos.
            if "text" in tool_args:
                output = process_expense.invoke(tool_args["text"])
            else:
                # Fallback por si el LLM estructura diferente
                output = process_expense.invoke(str(tool_args))

        elif tool_name == "save_thought":
            output = save_thought.invoke(tool_args)

        elif tool_name == "save_todo":
            output = save_todo.invoke(tool_args)

        else:
            output = "Error: Tool not found."

        results.append(
            ToolMessage(tool_call_id=call["id"], name=tool_name, content=str(output))
        )

    return {"messages": results}


# --- 4. Edges & Graph ---
def should_continue(state: AgentState) -> Literal["tools", END]:
    if state["messages"][-1].tool_calls:
        return "tools"
    return END


workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()
