"""
Script de Validación del Semantic Router
Moon AI v3.1

Prueba casos edge y verifica que los thresholds funcionen correctamente.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.router import classify_intent

# --- TEST CASES ---
test_cases = [
    # FINANCE (debería detectarse)
    ("Gasté 50 soles en almuerzo", "finance"),
    ("Pagué el alquiler", "finance"),
    ("Compré unas zapatillas de 200 soles", "finance"),
    ("Acabo de pagar 20 lucas", "finance"),
    
    # TASKS (debería detectarse)
    ("Recuérdame comprar leche mañana", "tasks"),
    ("Tengo que entregar el proyecto el viernes", "tasks"),
    ("Anota que debo llamar al banco", "tasks"),
    
    # PROFILE (debería detectarse)
    ("Me llamo Andy", "profile"),
    ("Soy programador", "profile"),
    ("Odio el brócoli", "profile"),
    ("Mi cumpleaños es el 15 de marzo", "profile"),
    
    # CHAT (debería detectarse o retornar None)
    ("Hola, ¿cómo estás?", None),  # Chat general
    ("¿Qué es un algoritmo?", None),  # Pregunta general
    ("Explícame qué es Python", None),  # Consulta
    ("Dame más detalle", None),  # Continuación
    
    # EDGE CASES (casos difíciles)
    ("¿Gasto mucho en comida?", None),  # Consulta (no finance simple)
    ("Recuérdame que gasté ayer", None),  # Pregunta sobre historial (no task)
    ("¿Sabes mi nombre?", None),  # Consulta de perfil (no escritura)
]

def run_tests():
    print("=" * 60)
    print("🧪 VALIDACIÓN DEL SEMANTIC ROUTER - Moon AI v3.1")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for user_input, expected in test_cases:
        result = classify_intent(user_input)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status} Input: '{user_input}'")
        print(f"   Expected: {expected}")
        print(f"   Got: {result}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADOS: {passed} passed, {failed} failed ({passed}/{len(test_cases)} - {passed/len(test_cases)*100:.1f}%)")
    print("=" * 60)
    
    if failed > 0:
        print("\n⚠️ RECOMENDACIONES:")
        print("- Ajustar thresholds en router.py si hay muchos falsos positivos/negativos")
        print("- Agregar más utterances de entrenamiento para las rutas problemáticas")
    else:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")

if __name__ == "__main__":
    run_tests()
