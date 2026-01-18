from datetime import datetime

from sqlalchemy.orm import Session

from src.core.database import Note, Task
from src.modules.knowledge.schemas import NoteEntry, TaskEntry


class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db

    def save_note(self, note_data: NoteEntry) -> dict:
        """
        Guarda un pensamiento o idea en la base de datos.
        """
        # Convertir lista de tags a string "tag1,tag2" para guardar en SQLite
        tags_str = ",".join(note_data.tags) if note_data.tags else ""

        new_note = Note(
            content=note_data.content,
            tags=tags_str,
            category=note_data.category,
            created_at=datetime.now(),  # Usamos hora local
        )

        self.db.add(new_note)
        self.db.commit()
        self.db.refresh(new_note)

        return {
            "status": "success",
            "id": new_note.id,
            "message": "Nota guardada correctamente en el cerebro.",
        }

    def save_task(self, task_data: TaskEntry) -> dict:
        """
        Guarda una tarea o recordatorio.
        """
        # Parsear la fecha si existe (El LLM nos da un string ISO)
        parsed_date = None
        if task_data.due_date:
            try:
                # Intentamos convertir el string ISO a objeto datetime
                parsed_date = datetime.fromisoformat(task_data.due_date)
            except ValueError:
                # Si falla, guardamos sin fecha (o manejamos el error)
                parsed_date = None

        new_task = Task(
            content=task_data.content,
            due_date=parsed_date,
            priority=task_data.priority,
            status="pending",
            created_at=datetime.now(),
        )

        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)

        return {
            "status": "success",
            "id": new_task.id,
            "type": "reminder",
            "due_date": str(parsed_date) if parsed_date else "No date",
            "message": f"Tarea agendada: {task_data.content}",
        }
