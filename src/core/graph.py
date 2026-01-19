# === FILE: src/core/graph.py ===
from dotenv import load_dotenv
from langgraph.graph import START, StateGraph

from src.core.database import init_db
from src.core.nodes import agent_node, should_continue, tool_node
from src.core.observer import observer_node
from src.core.state import AgentState  # <--- CAMBIO AQUÍ

load_dotenv()
init_db()

workflow = StateGraph(AgentState)

workflow.add_node("observer", observer_node)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "observer")

workflow.add_conditional_edges(
    "observer", should_continue, {"tools": "tools", "agent": "agent"}
)

workflow.add_edge("tools", "agent")
workflow.add_edge("agent", "__end__")

app = workflow.compile()
