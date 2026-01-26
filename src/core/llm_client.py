import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_chat_model(temperature=0.0, model_name="llama-3.3-70b-versatile"):
    """
    Cliente exclusivo para Groq (Velocity Architecture).
    Modelos típicos:
    - 'llama-3.3-70b-versatile' (Mondri / Razonamiento)
    - 'llama-3.1-8b-instant' (Router / Extracción rápida)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no encontrada en .env")

    return ChatGroq(
        model_name=model_name,
        temperature=temperature,
        groq_api_key=api_key,
    )
