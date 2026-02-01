import os

from dotenv import load_dotenv
from mem0 import Memory

load_dotenv()

# CONFIGURACIÓN
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "moon_hippocampus",
        },
    },
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.3-70b-versatile",
            "api_key": os.getenv("GROQ_API_KEY"),
            "temperature": 0.1,
            "max_tokens": 1000,
        },
    },
    "embedder": {
        "provider": "huggingface",
        "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"},
    },
}

# --- EL FIX DE VELOCIDAD (SINGLETON) ---
# Variable global para guardar la instancia
_memory_instance = None


def get_memory_client():
    global _memory_instance

    # Si ya existe, la devolvemos inmediatamente (0 segundos)
    if _memory_instance is not None:
        return _memory_instance

    # Si no existe, la creamos (solo pasa la primera vez)
    print("[INIT] Inicializando motor de memoria...")
    _memory_instance = Memory.from_config(config)
    return _memory_instance


def add_memory(user_id: str, text: str):
    try:
        m = get_memory_client()
        m.add(text, user_id=user_id)
        print("[MEMORY] Guardado exitoso")
    except Exception as e:
        print(f"[WARN] Error escribiendo memoria: {e}")


def get_memories(user_id: str, query: str = None):
    try:
        m = get_memory_client()
        if query:
            results = m.search(query, user_id=user_id)
        else:
            results = m.get_all(user_id=user_id)

        # Parche de robustez para formatos variados
        if isinstance(results, dict):
            results = results.get("results", list(results.values()))

        if not isinstance(results, list):
            return []

        cleaned_memories = []
        for r in results:
            if isinstance(r, dict) and "memory" in r:
                cleaned_memories.append(r["memory"])
            elif isinstance(r, str):
                cleaned_memories.append(r)

        return cleaned_memories

    except Exception as e:
        print(f"[WARN] Error leyendo memoria: {e}")
        return []
