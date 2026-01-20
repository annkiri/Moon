from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# --- MODELO PARA NOTAS (PENSAMIENTOS/IDEAS) ---
class NoteEntry(BaseModel):
    """
    Modelo para capturar pensamientos, ideas, referencias o reflexiones.
    NO tiene fecha de vencimiento ni acción inmediata.
    """

    content: str = Field(
        ..., description="El contenido principal de la nota o pensamiento."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Etiquetas para organizar (ej: 'idea', 'proyecto', 'reflexion').",
    )
    category: str = Field(
        default="general",
        description="Categoría general: 'personal', 'trabajo', 'moon', etc.",
    )


# --- MODELO PARA TAREAS (ACCIONES/RECORDATORIOS) ---
class TaskEntry(BaseModel):
    """
    Modelo para capturar acciones concretas, recordatorios o 'to-dos'.
    SIEMPRE implica una obligación futura.
    """

    content: str = Field(
        ..., description="La acción a realizar (ej: 'Comprar pan', 'Ir al doctor')."
    )
    due_date: Optional[str] = Field(
        None,
        description="Fecha de vencimiento en formato ISO 8601 (YYYY-MM-DD HH:MM:SS) inferida del contexto del usuario (ej: 'mañana' -> fecha de mañana).",
    )
    priority: str = Field(
        default="normal", description="Prioridad inferida: 'low', 'normal', 'high'."
    )
