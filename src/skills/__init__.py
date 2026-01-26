# --- src/skills/__init__.py ---

# En la arquitectura Velocity, Finance ya no es una 'Tool' estándar,
# sino un Nodo Especializado (Extractor).
# Por eso eliminamos la importación de 'finance'.

from src.skills.memory import save_thought, save_todo
from src.skills.profile import get_user_profile, update_user_profile

# Solo listamos las herramientas que sobreviven (Memoria y Perfil)
ALL_SKILLS = [
    save_thought,
    save_todo,
    update_user_profile,
    get_user_profile,
]
