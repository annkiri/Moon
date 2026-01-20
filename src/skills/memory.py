import json
from datetime import datetime
from typing import List, Optional

from langchain_core.tools import tool

from src.core.database import Note, SessionLocal, Task

# Importamos los Schemas para dárselos a Gemini
from src.modules.knowledge.schemas import NoteEntry, TaskEntry


@tool(args_schema=NoteEntry)
def save_thought(content: str, tags: List[str] = [], category: str = "general"):
    """
    Guarda una NOTA, pensamiento, idea o referencia estática.
    NO usar para tareas que requieren acción futura.
    """
    try:
        db = SessionLocal()

        # Convertimos la lista de tags a string para SQLite (ej: "idea,python")
        tags_str = ",".join(tags) if tags else ""

        new_note = Note(
            content=content, tags=tags_str, category=category, created_at=datetime.now()
        )

        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        db.close()

        return f"✅ Nota guardada (ID: {new_note.id})"

    except Exception as e:
        return f"❌ Error guardando nota: {str(e)}"


@tool(args_schema=TaskEntry)
def save_todo(content: str, due_date: Optional[str] = None, priority: str = "normal"):
    """
    Guarda una TAREA o recordatorio que requiere una acción futura.
    """
    try:
        db = SessionLocal()

        # Validación de fecha (Gemini nos manda string ISO, lo convertimos a objeto)
        parsed_date = None
        if due_date:
            try:
                parsed_date = datetime.fromisoformat(due_date)
            except ValueError:
                # Si falla el formato, guardamos sin fecha pero avisamos en el log
                print(f"[WARN] Formato de fecha inválido: {due_date}")
                parsed_date = None

        new_task = Task(
            content=content,
            due_date=parsed_date,
            priority=priority,
            status="pending",
            created_at=datetime.now(),
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        db.close()

        date_msg = f" para {parsed_date}" if parsed_date else ""
        return f"✅ Tarea agendada: {content}{date_msg}"

    except Exception as e:
        return f"❌ Error guardando tarea: {str(e)}"
