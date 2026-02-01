import os
from typing import List

import instructor
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

from src.models.finance import Transaction

load_dotenv()


class FinanceExtraction(BaseModel):
    """Resultado de extracción de gastos."""
    items: List[Transaction] = Field(default_factory=list)
    summary: str = Field(..., description="Resumen breve de lo extraído.")


# Cliente Groq con Instructor
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
instructor_client = instructor.from_groq(client, mode=instructor.Mode.JSON)


def extract_and_save_expense(user_input: str):
    """Extrae gastos usando Llama 3.1 8B."""
    import time
    from datetime import datetime
    
    print("[DEBUG] === INICIO FINANCE EXTRACTOR ===")
    extraction_start = time.time()
    
    try:
        model_name = "llama-3.1-8b-instant"
        print(f"[DEBUG] Modelo: {model_name}")
        
        # Fecha actual para el campo date
        today = datetime.now().strftime("%Y-%m-%d")
        
        resp = instructor_client.chat.completions.create(
            model=model_name,
            response_model=FinanceExtraction,
            messages=[
                {
                    "role": "system",
                    "content": f"""Extrae gastos del texto del usuario. Fecha de hoy: {today}

REGLAS CRÍTICAS:
1. Solo crea UNA transacción por cada GASTO REAL mencionado
2. CANTIDAD ≠ MONTO: "2 bebidas por 5.50" = 1 transacción de 5.50 (no 2 transacciones)
3. El MONTO es el número que viene después de palabras como: "por", "gasté", "pagué", "costó", "soles", "dólares"
4. Si dice "X items por Y soles", el monto es Y, no X
5. Si no hay monto explícito, NO crear transacción

EJEMPLOS:
- "compré 2 bebidas y gasté 5.50" → 1 transacción: bebidas, 5.50 PEN
- "100 soles en ventilador" → 1 transacción: ventilador, 100 PEN
- "2 soles en moto" → 1 transacción: moto, 2 PEN
- "compré 3 manzanas" → 0 transacciones (no hay monto)

Para cada gasto, extrae:
- amount: el monto MONETARIO (no cantidad de items)
- currency: PEN por defecto
- category: categoría inferida
- merchant: concepto o lugar
- date: {today}""",
                },
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
        )
        
        extraction_elapsed = time.time() - extraction_start
        print(f"[DEBUG] Inferencia completada en {extraction_elapsed:.3f}s")

        if not resp.items:
            print("[DEBUG] No se encontraron items")
            return {
                "status": "error",
                "summary": "No se detectó información financiera válida.",
            }

        # Guardar en SQLite
        from src.core.database import SessionLocal, TransactionModel
        
        db = SessionLocal()
        try:
            for item in resp.items:
                transaction = TransactionModel(
                    date=item.date,
                    amount=item.amount,
                    currency=item.currency,
                    category=item.category,
                    merchant=item.merchant,
                    notes=user_input
                )
                db.add(transaction)
            db.commit()
            
            print(f"[DEBUG] Guardados {len(resp.items)} items en SQLite")
            return {
                "status": "success",
                "summary": f"Registrados {len(resp.items)} gastos: {', '.join([t.merchant for t in resp.items])}",
                "data": [item.model_dump() for item in resp.items],
            }
        finally:
            db.close()

    except Exception as e:
        print(f"[ERROR] Durante extracción: {str(e)}")
        return {"status": "error", "summary": f"Error interno: {str(e)}"}
