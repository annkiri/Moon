from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from src.core.database import init_db
from src.core.nodes import (  # <--- IMPORTAMOS tasks_node
    agent_node,
    finance_node,
    router_node,
    tasks_node,
)
from src.core.state import AgentState

load_dotenv()
init_db()

workflow = StateGraph(AgentState)

# Nodos
workflow.add_node("router", router_node)
workflow.add_node("finance_assistant", finance_node)
workflow.add_node("tasks_assistant", tasks_node)  # <--- NUEVO
workflow.add_node("mondri_agent", agent_node)

# Entrada
workflow.add_edge(START, "router")


# Decisión
def route_decision(state: AgentState):
    intent = state.get("intent")
    if intent == "finance":
        return "finance_assistant"
    elif intent == "tasks":
        return "tasks_assistant"  # <--- NUEVO CAMINO
    else:
        return "mondri_agent"


workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "finance_assistant": "finance_assistant",
        "tasks_assistant": "tasks_assistant",
        "mondri_agent": "mondri_agent",
    },
)

# Salidas de asistentes vuelven a Mondri
workflow.add_edge("finance_assistant", "mondri_agent")
workflow.add_edge("tasks_assistant", "mondri_agent")  # <--- NUEVO RETORNO
workflow.add_edge("mondri_agent", END)

app = workflow.compile()
