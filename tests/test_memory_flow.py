import os
import sys
import time

# Ajuste de path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.messages import HumanMessage

from src.core.graph import app
from src.core.memory import get_memories  # Para verificar "tras bambalinas"


def run_memory_test():
    print("🧠 INICIANDO TEST DE MEMORIA (MOON HIPOCAMPO)")
    print("============================================")

    # PASO 1: ENSEÑAR (Write)
    # Intentamos guardar un dato nuevo
    print("\n📝 PASO 1: Inyectando recuerdo...")
    input1 = "Me llamo Andy y soy programador de Python."
    print(f"   👤 User: '{input1}'")

    # Ejecutamos el grafo
    state1 = {"messages": [HumanMessage(content=input1)]}
    for event in app.stream(state1):
        for key, value in event.items():
            if key == "mondri_agent" and "messages" in value:
                print(f"   🤖 Mondri: {value['messages'][0].content}")

    # Esperamos un poco para asegurar que Qdrant indexe (a veces toma ms)
    time.sleep(1)

    # PASO 2: VERIFICACIÓN INTERNA (Debug)
    print("\n🔍 PASO 2: Inspeccionando Qdrant...")
    memories = get_memories("andy_dev")
    if memories:
        print(f"   ✅ ÉXITO: Memoria encontrada en DB -> {memories}")
    else:
        print("   ❌ ERROR: Qdrant está vacío. Algo falló en el guardado.")

    # PASO 3: RECORDAR (Read)
    # Preguntamos algo que requiera ese recuerdo
    print("\n🗣️ PASO 3: Pregunta de validación...")
    input2 = "¿Qué lenguajes de programación manejo?"
    print(f"   👤 User: '{input2}'")

    state2 = {"messages": [HumanMessage(content=input2)]}
    for event in app.stream(state2):
        for key, value in event.items():
            if key == "mondri_agent":
                # Verificamos si hubo "Memory Hits" en el log
                if "debug_logs" in value:
                    print(f"   📊 Logs: {value['debug_logs']}")

                print(f"   🤖 Mondri: {value['messages'][0].content}")


if __name__ == "__main__":
    run_memory_test()
