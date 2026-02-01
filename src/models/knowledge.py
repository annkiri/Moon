from typing import List, Optional

from pydantic import BaseModel, Field


# --- MODELO NOTAS ---
class NoteEntry(BaseModel):
    content: str = Field(..., description="El contenido principal de la nota.")
    tags: List[str] = Field(
        default_factory=list,
        description="Lista de etiquetas clave (ej: ['python', 'idea']).",
    )
    category: str = Field(
        default="general", description="Categoría: personal, trabajo, dev, etc."
    )


# --- MODELO TAREAS ---
class TaskEntry(BaseModel):
    content: str = Field(..., description="La acción concreta a realizar.")
    due_date: Optional[str] = Field(
        None,
        description="Fecha ISO 8601 (YYYY-MM-DD HH:MM:SS). Si el usuario dice 'mañana', calcúlalo.",
    )
    priority: str = Field(
        default="normal", description="Prioridad: 'low', 'normal', 'high'."
    )
