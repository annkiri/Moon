"""
LLM Router - Clasificación de intenciones usando LLM
Moon AI v3.2

Reemplaza semantic-router por clasificación LLM para mejor generalización.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Cache para evitar re-clasificación
_last_classification = {"input": None, "result": None}


def classify_with_llm(user_input: str) -> str | None:
    """
    Clasifica la intención del usuario usando LLM.
    
    Returns:
        "finance" | "tasks" | "profile" | None (chat)
    """
    global _last_classification
    
    # Cache simple
    if _last_classification["input"] == user_input:
        return _last_classification["result"]
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """Clasifica el mensaje del usuario en UNA de estas categorías:

FINANCE: Gastos, compras, pagos, transferencias. DEBE tener monto o acción de dinero.
  - "Gasté 20 soles en taxi" → finance
  - "Pagué el alquiler" → finance
  - "Compré hamburguesa por 10 soles" → finance
  
TASKS: Recordatorios, tareas, alarmas, agendamientos.
  - "Recuérdame llamar a mamá" → tasks
  - "Pon alarma para las 7am" → tasks
  - "Tengo que ir al banco mañana" → tasks
  
PROFILE: Información personal permanente que el usuario QUIERE que recuerdes.
  - "Me llamo Andy" → profile (identidad)
  - "Soy programador" → profile (profesión)
  - "Me gusta el café" → profile (preferencias)
  - "Me encanta Python" → profile (intereses)
  - "Me está gustando Rust" → profile (intereses nuevos)
  - "Estoy aprendiendo X" → profile (habilidades)
  - "Mi color favorito es azul" → profile (preferencias)
  - "Soy de Perú" → profile (origen)
  
CHAT: Conversación general, preguntas, saludos, cualquier otra cosa.
  - "Hola, cómo estás" → chat
  - "¿Qué es Python?" → chat (pregunta general, no sobre el usuario)
  - "Cuéntame más" → chat

IMPORTANTE: Si el usuario comparte algo SOBRE SÍ MISMO (gustos, aprendizajes, datos personales), es PROFILE.

Responde SOLO con una palabra: finance, tasks, profile, o chat"""
                },
                {"role": "user", "content": user_input}
            ],
            temperature=0.0,
            max_tokens=10,
        )
        
        result = response.choices[0].message.content.strip().lower()
        
        # Normalizar resultado
        if result in ["finance", "tasks", "profile"]:
            intent = result
        else:
            intent = None  # chat
        
        # Guardar en cache
        _last_classification = {"input": user_input, "result": intent}
        
        return intent
        
    except Exception as e:
        print(f"[WARN] Router error: {e}")
        return None  # Fallback a chat


# Compatibilidad con la interfaz actual
def classify_intent(user_input: str) -> str | None:
    """
    Función de compatibilidad con el código existente.
    Usa LLM router internamente.
    """
    import time
    start = time.time()
    
    result = classify_with_llm(user_input)
    
    elapsed = (time.time() - start) * 1000
    
    if result:
        print(f"[ROUTER] Intencion: '{result}' ({elapsed:.1f}ms)")
    else:
        print(f"[ROUTER] Chat detectado ({elapsed:.1f}ms)")
    
    return result
