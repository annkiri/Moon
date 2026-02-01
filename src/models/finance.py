from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Transaction(BaseModel):
    amount: float = Field(..., description="The numeric amount of the transaction.")
    currency: str = Field(
        default="PEN", description="Currency ISO code (e.g., PEN, USD)."
    )
    category: str = Field(..., description="Inferred category (e.g., Food, Transport).")
    merchant: str = Field(
        ..., description="The entity paid (e.g., Uber, Restaurant) or the concept."
    )
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format.")
    notes: Optional[str] = Field(None, description="Additional context.")

    # --- REGLA 1: Nada de montos cero o negativos ---
    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is None or v <= 0:
            raise ValueError("El monto debe ser un número positivo mayor a 0.")
        return v

    # --- REGLA 2: Nada de conceptos vagos ---
    @field_validator("merchant")
    @classmethod
    def merchant_must_be_specific(cls, v):
        # Lista negra de palabras vagas
        vague_terms = ["algo", "cosas", "gasto", "compra", "lo de siempre", "nose"]
        if not v or len(v) < 2 or v.lower().strip() in vague_terms:
            raise ValueError(
                "El concepto/comercio es demasiado vago. Necesito saber QUÉ compraste o DÓNDE."
            )
        return v
