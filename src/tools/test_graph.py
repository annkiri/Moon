import sys
import os
import time  # <--- Importamos librería de tiempo

# Ajustar path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from langchain_core.messages import HumanMessage
from src.core.graph import app

def run_chat_test():
    print("--- INICIANDO TEST INTEGRAL DE MOON (Fase 1) ---")
    
    # --- Caso 1: Saludo simple ---
    print("\n[USER]: Hola Moon, ¿cómo estás?")
    initial_input = {"messages": [HumanMessage(content="Hola Moon, ¿cómo estás?")]}
    
    start_time = time.perf_counter() # ⏱️ Inicio cronómetro
    
    for event in app.stream(initial_input):
        for key, value in event.items():
            if key == "agent" and "messages" in value:
                 msg = value['messages'][0]
                 if msg.content:
                    print(f"[MOON]: {msg.content}")

    end_time = time.perf_counter() # ⏱️ Fin cronómetro
    elapsed = end_time - start_time
    print(f"⏱️ Tiempo total: {elapsed:.2f}s ({elapsed*1000:.0f}ms)")


    # --- Caso 2: Registro de Gasto ---
    print("\n" + "="*40)
    print("\n[USER]: Acabo de pagar 45 soles por un taxi al aeropuerto")
    expense_input = {"messages": [HumanMessage(content="Acabo de pagar 45 soles por un taxi al aeropuerto")]}
    
    start_time = time.perf_counter() # ⏱️ Inicio cronómetro
    
    for event in app.stream(expense_input):
        for key, value in event.items():
            # Mostramos detalles si es la herramienta ejecutándose
            if key == "tools":
                print(f"[SISTEMA INTERNO]: Herramienta ejecutada con éxito.")
            
            # Respuesta final del agente
            if key == "agent" and "messages" in value:
                 msg = value['messages'][0]
                 if msg.content:
                    print(f"[MOON]: {msg.content}")
    
    end_time = time.perf_counter() # ⏱️ Fin cronómetro
    elapsed = end_time - start_time
    print(f"⏱️ Tiempo total: {elapsed:.2f}s ({elapsed*1000:.0f}ms)")

if __name__ == "__main__":
    run_chat_test()