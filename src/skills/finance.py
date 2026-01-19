from langchain_core.tools import tool

from src.core.database import SessionLocal, TransactionModel
from src.modules.finance.service import FinanceService


@tool
def process_expense(text: str):
    """
    Use this skill ONLY when the user mentions spending money, buying something,
    or a financial transaction.
    Input: The raw text of the expense.
    """
    # Instanciamos el servicio
    service = FinanceService()

    try:
        print(f"[SKILL] Finance Triggered: {text}")
        data = service.extract_transaction_data(text)

        # Guardamos en SQLite
        db = SessionLocal()
        new_tx = TransactionModel(
            date=data.date,
            amount=data.amount,
            currency=data.currency,
            category=data.category,
            merchant=data.merchant,
            notes=data.notes,
        )
        db.add(new_tx)
        db.commit()
        db.refresh(new_tx)
        db.close()

        return f"Gasto registrado correctamente: {data.model_dump_json()}"

    except Exception as e:
        return f"Error procesando el gasto: {str(e)}"
