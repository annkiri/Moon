import os
from datetime import datetime, timedelta
from typing import Optional, List

import instructor
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

load_dotenv()


class Task(BaseModel):
    content: str = Field(..., description="La acción a realizar.")
    due_date: Optional[str] = Field(None, description="Fecha YYYY-MM-DD HH:MM.")
    priority: str = Field("normal", description="high, normal, low")


class TasksExtraction(BaseModel):
    tasks: List[Task] = Field(default_factory=list, description="Lista de tareas extraídas")
    summary: str = ""


client = Groq(api_key=os.getenv("GROQ_API_KEY"))
instructor_client = instructor.from_groq(client, mode=instructor.Mode.JSON)


def extract_and_save_task(user_input: str):
    try:
        # Calcular contexto de fecha
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        context_date = f"Hoy es {now.strftime('%A %Y-%m-%d %H:%M')}. Mañana es {tomorrow.strftime('%Y-%m-%d')}."

        resp = instructor_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_model=TasksExtraction,
            messages=[
                {
                    "role": "system",
                    "content": f"""Extrae TODAS las tareas/recordatorios del texto.
                    
{context_date}

Para cada tarea encontrada:
- content: la acción a realizar
- due_date: fecha y hora en formato YYYY-MM-DD HH:MM (si se menciona "mañana", usa {tomorrow.strftime('%Y-%m-%d')})
- priority: high, normal, o low

Si el usuario hace una PREGUNTA (ej: "¿Qué es X?"), NO extraigas tareas.
Si hay múltiples tareas, extrae TODAS.""",
                },
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
        )

        if not resp.tasks:
            return {"status": "ignored", "summary": "No se detectaron tareas claras."}

        # Guardar TODAS las tareas en SQLite
        from src.core.database import SessionLocal, Task as TaskModel
        
        db = SessionLocal()
        try:
            saved_tasks = []
            for task in resp.tasks:
                new_task = TaskModel(
                    content=task.content,
                    due_date=task.due_date,
                    priority=task.priority,
                    completed=False,
                    user_id="andy_dev"
                )
                db.add(new_task)
                saved_tasks.append(task.content)
            
            db.commit()
            
            return {
                "status": "success",
                "summary": f"Guardadas {len(resp.tasks)} tareas: {', '.join(saved_tasks)}",
                "data": [t.model_dump() for t in resp.tasks],
            }
        finally:
            db.close()

    except Exception as e:
        return {"status": "error", "summary": str(e)}


