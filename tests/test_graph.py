import os
import sys
import time

# Ajustar path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.messages import HumanMessage

from src.core.graph import app


def run_velocity_test():
    print("🚀 INICIANDO TEST DE VELOCIDAD (MOON v3.0)")
    print("==========================================")

    # --- CASO 1: CHAT GENERAL ---
    # Esperado: Router -> Mondri Agent
    print("\n💬 TEST 1: Conversación General")
    input_text = "Hola Moon, ¿cómo estás?"
    print(f"👤 User: '{input_text}'")

    start_time = time.perf_counter()
    state = {"messages": [HumanMessage(content=input_text)]}

    for event in app.stream(state):
        for key, value in event.items():
            # key es el nombre del nodo que acaba de ejecutarse
            print(f"   ⚡ Nodo activo: {key}")

            # Si el nodo devolvió logs, los mostramos
            if "debug_logs" in value:
                for log in value["debug_logs"]:
                    print(f"      📝 LOG: {log}")

            # Si es el agente final, mostramos la respuesta
            if key == "mondri_agent" and "messages" in value:
                msg = value["messages"][0]
                print(f"   🤖 MONDRI: {msg.content}")

    elapsed = time.perf_counter() - start_time
    print(f"⏱️ Tiempo total: {elapsed:.2f}s")

    # --- CASO 2: GASTO (VELOCITY TRACK) ---
    # Esperado: Router -> Finance Assistant -> Mondri Agent
    print("\n" + "=" * 40)
    print("\n💰 TEST 2: Registro de Gasto (Velocity Track)")
    input_text = "Acabo de pagar 45 soles por un taxi al aeropuerto"
    print(f"👤 User: '{input_text}'")

    start_time = time.perf_counter()
    state = {"messages": [HumanMessage(content=input_text)]}

    for event in app.stream(state):
        for key, value in event.items():
            print(f"   ⚡ Nodo activo: {key}")

            # Verificamos si el nodo de finanzas trabajó
            if key == "finance_assistant":
                # Normalmente Finance solo inyecta mensajes de sistema, no respuesta al usuario
                if "debug_logs" in value:
                    print(f"      ✅ EXTRACTOR: {value['debug_logs'][0]}")

            if key == "mondri_agent" and "messages" in value:
                msg = value["messages"][0]
                print(f"   🤖 MONDRI: {msg.content}")

    elapsed = time.perf_counter() - start_time
    print(f"⏱️ Tiempo total: {elapsed:.2f}s")


if __name__ == "__main__":
    run_velocity_test()
