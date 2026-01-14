from typing import Optional
from pydantic import BaseModel, Field

class Transaction(BaseModel):
    """
    Esquema para la extracción de transacciones financieras.
    Sigue las directrices estrictas de la documentación técnica sección 6.
    """
    amount: float = Field(..., description="Valor absoluto de la transacción.")
    currency: str = Field(default="PEN", description="Código ISO (PEN, USD). Por defecto: PEN.")
    category: str = Field(..., description="Categoría inferida (ej. 'Transporte', 'Antojos').")
    merchant: str = Field(..., description="Nombre del establecimiento o 'Varios'.")
    date: str = Field(..., description="Formato YYYY-MM-DD.")
    notes: Optional[str] = Field(None, description="Descripción original o resumen.")