import operator
from typing import Annotated, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # El historial de conversación (Chat)
    messages: Annotated[list[BaseMessage], add_messages]

    # Logs para depuración en UI (Tiempos, errores)
    debug_logs: Annotated[list[str], operator.add]

    # Intención detectada por el Router (finance, tasks, profile, None)
    intent: Optional[str]
