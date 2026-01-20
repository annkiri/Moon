from langchain_core.tools import tool

from src.core.database import SessionLocal, UserProfile

# Importamos el nuevo Schema
from src.modules.profile.schemas import UserProfileEntry


@tool(args_schema=UserProfileEntry)
def update_user_profile(key: str, value: str, category: str = "general"):
    """
    Guarda o actualiza un HECHO PERMANENTE sobre el usuario (Upsert).
    Use 'snake_case' para la key.
    """
    print(f"[SKILL] Updating Profile: {key} -> {value}")
    session = SessionLocal()
    try:
        # Lógica Upsert: Buscar si existe
        existing_fact = session.query(UserProfile).filter_by(key=key).first()

        if existing_fact:
            existing_fact.value = value
            existing_fact.category = category
            msg = f"✅ Dato actualizado: '{key}' ahora es '{value}'."
        else:
            new_fact = UserProfile(key=key, value=value, category=category)
            session.add(new_fact)
            msg = f"✅ Nuevo dato aprendido: '{key}' es '{value}'."

        session.commit()
        return msg

    except Exception as e:
        session.rollback()
        return f"❌ Error actualizando perfil: {str(e)}"
    finally:
        session.close()


@tool
def get_user_profile(category: str = None):
    """
    Lee la información guardada sobre el usuario.
    Útil para responder preguntas como '¿Sabes mi nombre?' o personalizar respuestas.
    """
    session = SessionLocal()
    try:
        query = session.query(UserProfile)
        if category:
            query = query.filter_by(category=category)

        facts = query.all()
        if not facts:
            return "No hay datos de perfil guardados."

        # Formato limpio para que el LLM lo lea fácil
        return "\n".join([f"- {f.key}: {f.value} ({f.category})" for f in facts])
    finally:
        session.close()
