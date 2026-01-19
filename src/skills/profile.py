import json

from langchain_core.tools import tool

from src.core.database import SessionLocal, UserProfile


@tool
def update_user_profile(key: str, value: str, category: str = "general"):
    """
    Use this tool ONLY to save PERMANENT SINGLE FACTS about the user.
    Suitable for: Names, birthdays, specific preferences (one item), physical traits, location.

    NOT suitable for: Lists of movies, thoughts, random ideas, or temporary states.

    Args:
        key: A snake_case unique identifier (e.g. 'user_name', 'favorite_color', 'home_city').
        value: The factual value to store (e.g. 'Veronica', 'Blue', 'Lima').
        category: Optional grouping (default: 'general').
    """
    print(f"[SKILL] Updating Profile Fact: {key} -> {value}")
    session = SessionLocal()
    try:
        # Lógica de "Upsert" (Actualizar si existe, Crear si no)
        existing_fact = session.query(UserProfile).filter_by(key=key).first()

        if existing_fact:
            old_val = existing_fact.value
            existing_fact.value = value
            existing_fact.category = category
            msg = f"Updated fact '{key}': was '{old_val}', now '{value}'."
        else:
            new_fact = UserProfile(key=key, value=value, category=category)
            session.add(new_fact)
            msg = f"Learned new fact: '{key}' is '{value}'."

        session.commit()
        return msg

    except Exception as e:
        session.rollback()
        return f"Error updating profile: {str(e)}"
    finally:
        session.close()


@tool
def get_user_profile(category: str = None):
    """
    Use this tool to READ what you know about the user's permanent profile.
    Useful when you need to answer personal questions like 'Do you know my name?' or 'What do I like?'.
    """
    session = SessionLocal()
    try:
        query = session.query(UserProfile)
        if category:
            query = query.filter_by(category=category)

        facts = query.all()
        if not facts:
            return "No profile data found."

        # Formato legible para el LLM
        return "\n".join([f"- {f.key}: {f.value} ({f.category})" for f in facts])
    finally:
        session.close()
