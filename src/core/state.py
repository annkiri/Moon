# === FILE: src/core/state.py ===
import operator
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # NUEVO: Lista acumulativa de strings para logs de tiempos y errores
    debug_logs: Annotated[list[str], operator.add]
