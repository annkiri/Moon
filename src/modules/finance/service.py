import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.modules.finance.schemas import Transaction

class FinanceService:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def extract_transaction_data(self, user_text: str) -> Transaction:
        """
        Procesa el texto del usuario y extrae una transacción estructurada.
        """
        
        # PROMPT SIMPLIFICADO Y FLEXIBLE
        # En lugar de reglas duras de jergas, definimos el contexto cultural.
        system_prompt = """
        Eres un asistente de finanzas personales.
        Tu tarea es estructurar datos de gastos a partir de lenguaje natural.
        
        Contexto:
        - Ubicación: Perú (entender modismos locales si aparecen).
        - Moneda base: PEN (Soles).
        - Fecha base: Hoy (2026-01-14).
        
        Instrucciones:
        1. Identifica el monto y la moneda. Si no es explícita, asume PEN.
        2. Infiere la categoría según el contexto del comercio o actividad.
        3. Mantén la descripción (notas) breve y fiel al original.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}"),
        ])

        structured_llm = self.llm.with_structured_output(Transaction)
        chain = prompt | structured_llm

        return chain.invoke({"text": user_text})