from src.skills.finance import process_expense
from src.skills.memory import save_thought, save_todo
from src.skills.profile import get_user_profile, update_user_profile

# Ahora el cerebro tiene 5 manos
ALL_SKILLS = [
    process_expense,
    save_thought,
    save_todo,
    update_user_profile,
    get_user_profile,
]
