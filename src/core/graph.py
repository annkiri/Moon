import os
from typing import Annotated, TypedDict, Literal

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

from src.modules.finance.service import FinanceService
from src.core.prompts import MOON_SYS_PROMPT  # <--- Importamos la personalidad

from src.core.database import SessionLocal, TransactionModel, init_db # <--- NUEVO

load_dotenv()

# Inicializamos la DB al arrancar el script
init_db()

# --- 1. Estado ---
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# --- 2. Tools ---
@tool
def process_expense(text: str):
    """
    Extracts finance transaction details and SAVES them to the database.
    """
    print(f"[INFO] Tool 'process_expense' triggered: {text}")
    service = FinanceService()
    
    try:
        # 1. Extracción con IA
        data = service.extract_transaction_data(text)
        
        # 2. Guardado en Base de Datos (Persistencia)
        db = SessionLocal()
        new_tx = TransactionModel(
            date=data.date,
            amount=data.amount,
            currency=data.currency,
            category=data.category,
            merchant=data.merchant,
            notes=data.notes
        )
        db.add(new_tx)
        db.commit()
        db.refresh(new_tx) # Obtenemos el ID generado
        db.close()
        
        print(f"[DB] Transaction saved with ID: {new_tx.id}")
        
        # Devolvemos JSON para que Moon lo lea, confirmando el guardado
        return data.model_dump_json()
        
    except Exception as e:
        return f"Error processing expense: {str(e)}"

# --- 3. Nodos ---

def agent_node(state: AgentState):
    # Temperatura 0.7 para balancear creatividad sarcástica con obediencia de herramientas
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7, 
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    tools = [process_expense]
    llm_with_tools = llm.bind_tools(tools)
    
    # Inyectamos la personalidad desde el archivo externo
    system_msg = SystemMessage(content=MOON_SYS_PROMPT)
    
    messages = [system_msg] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return {"messages": []}
    
    results = []
    for call in last_message.tool_calls:
        if call["name"] == "process_expense":
            tool_output = process_expense.invoke(call)
            results.append(ToolMessage(
                tool_call_id=call["id"],
                name=call["name"],
                content=str(tool_output)
            ))
            
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