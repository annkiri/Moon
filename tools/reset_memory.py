import os
import sys

from dotenv import load_dotenv
from mem0 import Memory
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Ajuste de path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

load_dotenv()


def force_create_collection():
    print("[RESET] Iniciando creacion forzada de coleccion (384 dims)...")

    # 1. CONEXIÓN A QDRANT
    try:
        client = QdrantClient(host="localhost", port=6333)
        collection_name = "moon_hippocampus"

        # 2. BORRADO Y RECREACIÓN EXPLÍCITA
        # Esto le ordena a Qdrant: "Crea una caja que SOLO acepte vectores de tamaño 384"
        print(f"[RESET] Re-creando coleccion '{collection_name}' con size=384...")

        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print("[OK] Coleccion creada manualmente.")

    except Exception as e:
        print(f"[ERROR] Conectando a Qdrant: {e}")
        return

    # 3. INICIALIZACIÓN DE MEM0
    # Ahora Mem0 encontrará la colección existente y NO intentará crear una de 1536.
    print("\n[INIT] Inicializando Mem0...")

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
            },
        },
        "embedder": {
            "provider": "huggingface",
            "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"},
        },
    }

    try:
        m = Memory.from_config(config)

        # 4. PRUEBA DE ESCRITURA
        print("[TEST] Intentando guardar recuerdo...")
        # Esto debería funcionar porque los vectores generados (384) ahora sí caben en la colección (384)
        m.add("Soy Andy y forcé la configuración de memoria.", user_id="andy_dev")
        print("[OK] Recuerdo guardado exitosamente.")

        # 5. PRUEBA DE LECTURA
        print("[TEST] Verificando lectura...")
        memories = m.get_all(user_id="andy_dev")
        texts = [mem["memory"] for mem in memories]
        print(f"[OK] Memoria leida: {texts}")

    except Exception as e:
        print(f"[ERROR] Fallo final: {e}")


if __name__ == "__main__":
    force_create_collection()
