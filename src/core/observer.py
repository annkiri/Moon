import time
from datetime import datetime

from langchain_core.messages import SystemMessage

from src.core.llm_client import get_chat_model
from src.core.state import AgentState
from src.skills import ALL_SKILLS

# PROMPT ACTUALIZADO PARA FUNCTION CALLING NATIVO
OBSERVER_PROMPT = """
ROLE: Background Data Observer.
OBJECTIVE: Analyze the conversation and call Tools ONLY if structured data can be extracted.

--- CONTEXT ---
CURRENT TIME: {current_time}

--- INSTRUCTIONS ---
1. YOUR JOB: Look for specific intents (Finance, Tasks, Ideas, Profile).
2. EXTRACTION: DO NOT pass raw text to tools. You must extract the exact arguments (amount, merchant, key, value, etc.).
3. CHIT-CHAT: If the user is just saying hello or asking questions, RETURN EMPTY (do not call tools).
4. MULTI-ACTION: If the user lists multiple items, call the tool multiple times in parallel.

--- SPECIFIC DOMAINS ---

[FINANCE]
- Trigger: Spending money, purchases.
- Tool: `process_expense`
- Requirement: You MUST extract 'amount', 'merchant', and infer 'category'.

[PROFILE]
- Trigger (WRITE): User mentions their name, job, tech stack, or preferences.
- Tool: `update_user_profile` (Extract 'key' and 'value').
- Trigger (READ): User asks "Who am I?", "Do you know my name?", or asks about stored info.
- Tool: `get_user_profile` (Extract 'category' if specific, or None).

[TASKS & IDEAS]
- Trigger: Future plans (Tasks) or abstract thoughts (Ideas).
- Tools: `save_todo` or `save_thought`.

"""


def observer_node(state: AgentState):
    # Gemini 3 Flash con temperatura 0 es excelente llenando formularios (Schemas)
    llm = get_chat_model(
        temperature=0.0, provider="gemini", model_name="gemini-3-flash-preview"
    )

    # VINCULAMOS LAS SKILLS (Aquí viajan tus Schemas de Pydantic hacia Gemini)
    llm_with_tools = llm.bind_tools(ALL_SKILLS)

    last_user_msg = state["messages"][-1]

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_prompt = OBSERVER_PROMPT.format(current_time=current_time)

    system_msg = SystemMessage(content=formatted_prompt)
    messages = [system_msg, last_user_msg]

    start_time = time.time()
    try:
        # Gemini analiza y decide si llamar a una función o no
        response = llm_with_tools.invoke(messages)
        duration = time.time() - start_time

        # Log para depuración
        return {
            "messages": [response],
            "debug_logs": [f"👀 [Observer] Análisis en {duration:.2f}s"],
        }
    except Exception as e:
        return {"messages": [], "debug_logs": [f"⚠️ Error Observer: {e}"]}
