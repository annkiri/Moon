import os
from functools import lru_cache

# IMPORTS DE MODELOS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

try:
    from langchain_xai import ChatXAI
except ImportError:
    ChatXAI = None  # Fallback si no está instalado


def get_chat_model(temperature=0.0, provider=None, model_name=None):
    """
    Fábrica universal de modelos (Edición 2026).
    Soporta: Gemini 3 Flash, Grok 4.1 Fast y Llama 3 (Groq).
    """
    # Si no especifican proveedor, usamos el del .env o 'gemini' por defecto
    target_provider = provider or os.getenv("AI_PROVIDER", "gemini")
    target_provider = target_provider.lower()

    # --- OPCIÓN 1: GOOGLE GEMINI (Tu Observer) ---
    if target_provider == "gemini":
        default_model = "gemini-3-flash-preview"
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada en .env")

        return ChatGoogleGenerativeAI(
            model=model_name or default_model,
            temperature=temperature,
            google_api_key=api_key,
            convert_system_message_to_human=True,
        )

    # --- OPCIÓN 2: XAI GROK (Legacy / Fallback) ---
    elif target_provider == "grok":
        if ChatXAI is None:
            raise ImportError("Instala langchain-xai: pip install langchain-xai")

        default_model = "grok-4-1-fast"
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError("XAI_API_KEY no encontrada en .env")

        return ChatXAI(
            model=model_name or default_model,
            temperature=temperature,
            xai_api_key=api_key,
        )

    # --- OPCIÓN 3: GROQ (Nuevo Motor de Velocidad) ---
    elif target_provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY no encontrada en .env")

        return ChatGroq(
            model_name=model_name or "llama-3.3-70b-versatile",
            temperature=temperature,
            groq_api_key=api_key,  # Corrección: nombre exacto del parámetro
        )

    else:
        raise ValueError(f"Proveedor '{target_provider}' no soportado.")
