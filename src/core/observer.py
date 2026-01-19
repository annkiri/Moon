from datetime import datetime

from langchain_core.messages import SystemMessage

from src.core.llm_client import get_chat_model
from src.core.state import AgentState
from src.skills import ALL_SKILLS

# PROMPT MEJORADO: Lógica de separación de gastos (Split)
OBSERVER_PROMPT = """
ROLE: Background Data Observer.
OBJECTIVE: Scan the user's latest message and decide if a Tool must be called.

--- CONTEXT ---
CURRENT TIME: {current_time}

--- DECISION RULES ---
1. USER PROFILE:
   - Capture PERMANENT facts: user_name, birthday, emails, skills, likes/dislikes.
   - Use SNAKE_CASE keys.

2. TASKS:
   - If user mentions a plan/date -> Call `save_todo`.
   - Calculate 'due_date' strictly as 'YYYY-MM-DD HH:MM:SS'.

3. MONEY (CRITICAL - SPLIT ACTIONS):
   - If user mentions MULTIPLE expenses, you MUST call `process_expense` multiple times (once per item).
   - DO NOT send the full sentence to the tool. Split it.
   - Example Input: "Taxi 10 and Food 20"
   - Correct Output: Call `process_expense("Taxi 10")` AND Call `process_expense("Food 20")`.
   - Incorrect Output: Call `process_expense("Taxi 10 and Food 20")`.

4. IDEAS:
   - Abstract thoughts or project ideas -> Call `save_thought`.

OUTPUT:
- Call the tool via JSON or return EMPTY if just chit-chat.
- DO NOT generate text responses.
"""


def observer_node(state: AgentState):
    # Usamos el modelo que confirmaste que funciona
    llm = get_chat_model(
        temperature=0.0, provider="gemini", model_name="gemini-3-flash-preview"
    )

    llm_with_tools = llm.bind_tools(ALL_SKILLS)
    last_user_msg = state["messages"][-1]

    # Inyección de Tiempo
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_prompt = OBSERVER_PROMPT.format(current_time=current_time)

    system_msg = SystemMessage(content=formatted_prompt)
    messages = [system_msg, last_user_msg]

    try:
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        print(f"⚠️ Error en Observer: {e}")
        return {"messages": []}
