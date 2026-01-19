# === FILE: src/modules/finance/service.py ===
from langchain_core.prompts import ChatPromptTemplate

# Importamos tu nuevo cliente universal
from src.core.llm_client import get_chat_model
from src.modules.finance.schemas import Transaction


class FinanceService:
    def __init__(self):
        # Solicitamos el modelo con temperatura 0 para precisión
        self.llm = get_chat_model(temperature=0)

    def extract_transaction_data(self, user_text: str) -> Transaction:
        """
        Procesa el texto del usuario y extrae una transacción estructurada.
        """

        system_prompt = """
        Eres un asistente de finanzas personales.
        Tu tarea es estructurar datos de gastos a partir de lenguaje natural.

        Contexto:
        - Ubicación: Perú (entender modismos locales si aparecen).
        - Moneda base: PEN (Soles).
        - Fecha base: Hoy (usa la fecha actual del sistema si es necesario).

        Instrucciones:
        1. Identifica el monto y la moneda. Si no es explícita, asume PEN.
        2. Infiere la categoría según el contexto del comercio o actividad.
        3. Mantén la descripción (notes) breve y fiel al original.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{text}"),
            ]
        )

        # Usamos el modelo agnóstico
        structured_llm = self.llm.with_structured_output(Transaction)  # type: ignore
        chain = prompt | structured_llm

        return chain.invoke({"text": user_text})  # type: ignore
