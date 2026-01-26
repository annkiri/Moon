import os
from datetime import datetime, timedelta
from typing import Optional

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
    task: Optional[Task] = None
    summary: str


client = Groq(api_key=os.getenv("GROQ_API_KEY"))
instructor_client = instructor.from_groq(client, mode=instructor.Mode.JSON)


def extract_and_save_task(user_input: str):
    try:
        # Calcular contexto de fecha
        now = datetime.now()
        context_date = f"Hoy es {now.strftime('%A %Y-%m-%d %H:%M')}"

        resp = instructor_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=TasksExtraction,
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    Eres un asistente ejecutivo. {context_date}.

                    REGLAS CRÍTICAS:
                    1. Si el usuario hace una PREGUNTA (ej: "¿Qué es un algoritmo?", "¿Cómo funciona X?"), NO extraigas tarea. Devuelve task=None.
                    2. Solo extrae tarea si hay una INTENCIÓN DE ACCIÓN (ej: "Recuérdame", "Tengo que", "Agenda").
                    3. Si no hay tarea clara, task debe ser null.
                    """,
                },
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
        )

        if not resp.task:
            return {"status": "ignored", "summary": "No se detectó una tarea clara."}

        # Simulación de guardado (ID 999 para pruebas)
        return {
            "status": "success",
            "summary": f"Tarea: {resp.task.content} ({resp.task.due_date})",
            "data": resp.task.model_dump(),
        }

    except Exception as e:
        return {"status": "error", "summary": str(e)}
