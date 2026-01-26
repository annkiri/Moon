import os
from typing import List, Optional

import instructor
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field, field_validator

load_dotenv()


# --- MODELOS DE DATOS ---
class Transaction(BaseModel):
    amount: float = Field(..., description="Monto numérico.")
    currency: str = Field(default="PEN", description="Moneda (PEN, USD).")
    category: str = Field(..., description="Categoría inferida.")
    merchant: str = Field(..., description="Comercio o concepto.")
    date: str = Field(..., description="Fecha YYYY-MM-DD.")
    notes: Optional[str] = Field(None, description="Contexto extra.")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Monto debe ser positivo")
        return v


class FinanceExtraction(BaseModel):
    items: List[Transaction] = Field(default_factory=list)
    summary: str = Field(..., description="Resumen breve de lo extraído.")


# --- CLIENTE ---
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
instructor_client = instructor.from_groq(client, mode=instructor.Mode.JSON)


def extract_and_save_expense(user_input: str):
    """Extrae gastos usando Llama 3 con defensa contra alucinaciones."""
    try:
        resp = instructor_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=FinanceExtraction,
            messages=[
                {
                    "role": "system",
                    "content": """
                    Eres un contador experto y estricto.
                    Tu trabajo es extraer gastos ESTRUCTURADOS del texto del usuario.

                    REGLAS CRÍTICAS (ANTI-ALUCINACIÓN):
                    1. Solo extrae si hay un MONTO CLARO y un CONCEPTO.
                    2. Si el usuario dice "más detalle", "explícame", u opina: DEVUELVE LISTA VACÍA [].
                    3. NO inventes gastos que no están en el texto actual.
                    4. Si no hay gastos, el summary debe decir "No se detectaron gastos".
                    """,
                },
                {"role": "user", "content": f"Texto actual: '{user_input}'"},
            ],
            temperature=0.0,  # Temperatura 0 para máxima precisión
        )

        # Filtro manual post-LLM
        if not resp.items:
            return {
                "status": "error",
                "summary": "No se detectó información financiera válida.",
            }

        # Aquí iría la lógica de guardado en Supabase (simulada por ahora)
        return {
            "status": "success",
            "summary": f"Registrados {len(resp.items)} gastos: {', '.join([t.merchant for t in resp.items])}",
            "data": [item.model_dump() for item in resp.items],
        }

    except Exception as e:
        return {"status": "error", "summary": f"Error interno: {str(e)}"}
