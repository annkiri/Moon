import os
import sys
import time

# Ajuste de path para que encuentre tus módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.messages import HumanMessage

from src.core.graph import app

# --- LISTA DE ESCENARIOS A PROBAR ---
SCENARIOS = [
    {"name": "1. GASTO SIMPLE", "input": "Gaste 15 soles en una hamburguesa."},
    {
        "name": "2. GASTO MÚLTIPLE (Prueba de Fuego)",
        "input": "apunta, gaste 5 soles en desayunos y 10 soles en pasaje",
    },
    {
        "name": "3. GASTO CON JERGA (Cocos)",
        "input": "Acabo de pagar la mensualidad del gym, fueron 120 cocos.",
    },
    {"name": "4. TAREA SIMPLE", "input": "Tengo que llamar al banco."},
    {
        "name": "5. TAREA CON FECHA Y COMILLAS",
        "input": '"Recuérdame comprar leche mañana a las 8am."',
    },
    {"name": "6. RUIDO + SALUDO", "input": "Hola mon , gaste 20 soles en taxi"},
    {"name": "7. PERFIL (Identidad)", "input": "Me llamo Andy y soy programador."},
]


def run_tests():
    print("🚀 INICIANDO BATERÍA DE PRUEBAS AUTOMÁTICAS (MOON VELOCITY)")
    print("===========================================================")

    for i, scenario in enumerate(SCENARIOS):
        name = scenario["name"]
        text = scenario["input"]

        print(f"\n🧪 TEST {name}")
        print(f"   📥 Input: '{text}'")

        state = {"messages": [HumanMessage(content=text)]}
        start_time = time.perf_counter()

        try:
            # Ejecutamos el grafo
            for event in app.stream(state):
                for node_name, value in event.items():
                    # 1. Detectar Intención (Router)
                    if node_name == "router":
                        intent = value.get("intent", "Desconocido")
                        print(f"   ⚡ Router: Detectó '{intent}'")

                    # 2. Detectar Logs de Extractores (Finanzas/Tareas)
                    if "debug_logs" in value:
                        for log in value["debug_logs"]:
                            # Usamos íconos para diferenciar éxito de error
                            icon = "✅" if "Éxito" in log or "exitosa" in log else "❌"
                            print(f"   {icon} Skill: {log}")

                    # 3. Detectar Respuesta de Mondri
                    if node_name == "mondri_agent" and "messages" in value:
                        response = value["messages"][0].content
                        # Cortamos la respuesta para no llenar la pantalla (solo los primeros 100 chars)
                        preview = response[:100].replace("\n", " ") + "..."
                        print(f"   🤖 Mondri: {preview}")

            elapsed = time.perf_counter() - start_time
            print(f"   ⏱️ Tiempo: {elapsed:.2f}s")

        except Exception as e:
            print(f"   🔥 ERROR FATAL: {e}")

    print("\n===========================================================")
    print("🏁 PRUEBAS FINALIZADAS")


if __name__ == "__main__":
    run_tests()
