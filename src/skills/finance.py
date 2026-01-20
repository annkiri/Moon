from datetime import datetime

from langchain_core.tools import tool

from src.core.database import SessionLocal, TransactionModel

# IMPORTAMOS EL SCHEMA (Tu red de seguridad)
from src.modules.finance.schemas import Transaction


@tool(args_schema=Transaction)
def process_expense(
    amount: float,
    merchant: str,
    category: str,
    currency: str = "PEN",
    date: str = None,
    notes: str = None,
):
    """
    Registra un gasto en la base de datos.
    El Observer debe extraer MONTO, COMERCIO y CATEGORÍA antes de llamar a esto.
    """
    try:
        # Abrimos DB
        db = SessionLocal()

        # Validación de fecha por si Gemini la manda vacía
        final_date = date if date else datetime.now().strftime("%Y-%m-%d")

        # Guardado directo (Velocidad pura)
        new_tx = TransactionModel(
            date=final_date,
            amount=amount,
            currency=currency,
            category=category,
            merchant=merchant,
            notes=notes,
        )

        db.add(new_tx)
        db.commit()
        db.refresh(new_tx)
        db.close()

        return f"✅ Gasto guardado: {amount} {currency} en {merchant} ({category})"

    except Exception as e:
        return f"❌ Error guardando gasto: {str(e)}"
