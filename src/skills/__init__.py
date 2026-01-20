from src.skills.finance import process_expense
from src.skills.memory import save_thought, save_todo

# Asegúrate de que estén estas dos:
from src.skills.profile import get_user_profile, update_user_profile

ALL_SKILLS = [
    process_expense,
    save_thought,
    save_todo,
    update_user_profile,
    get_user_profile,
]
