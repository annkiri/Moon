import json
from typing import Optional

from langchain_core.tools import tool

from src.core.database import SessionLocal
from src.modules.knowledge.schemas import NoteEntry, TaskEntry
from src.modules.knowledge.service import KnowledgeService


@tool
def save_thought(content: str, tags: str = "", category: str = "general"):
    """
    Use this tool to save generic thoughts, ideas, references, or static information.
    NOT for tasks or things to do later.
    Args:
        content: The main text of the note.
        tags: Comma-separated keywords (e.g. "ideas, projects").
        category: General category (default: 'general').
    """
    print(f"[SKILL] Memory (Thought) Triggered: {content}")
    try:
        db = SessionLocal()
        service = KnowledgeService(db)
        # Limpieza de tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else []

        note_data = NoteEntry(content=content, tags=tag_list, category=category)
        result = service.save_note(note_data)
        db.close()
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error guardando nota: {str(e)}"


@tool
def save_todo(content: str, due_date: Optional[str] = None, priority: str = "normal"):
    """
    Use this tool to save TASKS, reminders, or actions that need to be done in the future.
    Args:
        content: The action to perform (e.g., "Buy milk").
        due_date: ISO 8601 date string or None (inferred from user context).
        priority: 'normal', 'high', or 'low'.
    """
    print(f"[SKILL] Memory (Task) Triggered: {content} | Due: {due_date}")
    try:
        db = SessionLocal()
        service = KnowledgeService(db)

        task_data = TaskEntry(content=content, due_date=due_date, priority=priority)
        result = service.save_task(task_data)
        db.close()
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error guardando tarea: {str(e)}"
