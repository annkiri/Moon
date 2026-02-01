"""
Test de los 3 Fixes Críticos - Moon AI v3.1

Valida:
1. Daily.md guarda mensaje real del usuario (no system)
2. Qdrant se activa con patrones inteligentes
3. Tasks persisten en SQLite
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from langchain_core.messages import HumanMessage, SystemMessage
from src.core.graph import app
from src.core.database import SessionLocal, Task as TaskModel
import json

def test_fix1_daily_md():
    """Test Fix 1: Daily.md guarda mensaje real del usuario"""
    print("\n" + "="*60)
    print("🧪 TEST FIX 1: Daily.md guarda mensaje REAL del usuario")
    print("="*60)
    
    user_input = "Gasté 25 soles en almuerzo"
    messages = [HumanMessage(content=user_input)]
    
    result = app.invoke({"messages": messages})
    
    # Leer daily.jsonl
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = Path(__file__).parent / "daily_context" / f"{today}.jsonl"
    
    if daily_file.exists():
        with open(daily_file, "r") as f:
            lines = f.readlines()
            last_entry = json.loads(lines[-1])
            
            print(f"Usuario dijo: '{user_input}'")
            print(f"Daily.md guardó: '{last_entry['user']}'")
            
            if "[SYSTEM]" in last_entry['user']:
                print("❌ FAIL: Daily.md guardó mensaje de SISTEMA")
                return False
            elif user_input in last_entry['user']:
                print("✅ PASS: Daily.md guardó mensaje REAL del usuario")
                return True
            else:
                print("⚠️ WARN: Mensaje guardado difiere del original")
                return False
    else:
        print("❌ FAIL: Archivo daily.md no existe")
        return False

def test_fix2_intelligent_qdrant():
    """Test Fix 2: Qdrant detecta patrones permanentes"""
    print("\n" + "="*60)
    print("🧪 TEST FIX 2: Detección inteligente para Qdrant")
    print("="*60)
    
    test_cases = [
        ("Me llamo Roberto", True, "nombre propio"),
        ("Me gusta el té verde", True, "preferencia"),
        ("Mi madre se llama Ana", True, "relación familiar"),
        ("Hoy estoy cansado", False, "estado temporal"),
        ("Gasté 20 soles", False, "transacción"),
        ("¿Qué hora es?", False, "pregunta casual"),
    ]
    
    from src.core.nodes import _should_save_to_longterm
    
    passed = 0
    for msg, expected, reason in test_cases:
        result = _should_save_to_longterm(msg, intent=None)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        
        print(f"{status} '{msg}' → {result} (esperado: {expected}) - {reason}")
    
    print(f"\n📊 Resultado: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.0f}%)")
    return passed == len(test_cases)

def test_fix3_task_persistence():
    """Test Fix 3: Tasks se guardan en SQLite"""
    print("\n" + "="*60)
    print("🧪 TEST FIX 3: Persistencia de Tasks en SQLite")
    print("="*60)
    
    # Borrar tasks previos de test
    db = SessionLocal()
    db.query(TaskModel).filter(TaskModel.content.like("%TEST%")).delete()
    db.commit()
    
    # Crear tarea de prueba
    user_input = "Recuérdame hacer TEST de persistencia mañana"
    messages = [HumanMessage(content=user_input)]
    
    result = app.invoke({"messages": messages})
    
    # Verificar en SQLite
    tasks = db.query(TaskModel).filter(TaskModel.content.like("%TEST%")).all()
    db.close()
    
    if len(tasks) > 0:
        print(f"✅ PASS: Tarea guardada en SQLite")
        print(f"   ID: {tasks[0].id}")
        print(f"   Content: {tasks[0].content}")
        print(f"   Due Date: {tasks[0].due_date}")
        return True
    else:
        print(f"❌ FAIL: No se encontró tarea en SQLite")
        return False

if __name__ == "__main__":
    print("\n🧪 MOON AI v3.1 - TESTS DE FIXES CRÍTICOS")
    
    results = []
    
    try:
        results.append(("Fix 1: Daily.md", test_fix1_daily_md()))
    except Exception as e:
        print(f"❌ Error en Fix 1: {e}")
        results.append(("Fix 1: Daily.md", False))
    
    try:
        results.append(("Fix 2: Qdrant Inteligente", test_fix2_intelligent_qdrant()))
    except Exception as e:
        print(f"❌ Error en Fix 2: {e}")
        results.append(("Fix 2: Qdrant Inteligente", False))
    
    try:
        results.append(("Fix 3: Task Persistence", test_fix3_task_persistence()))
    except Exception as e:
        print(f"❌ Error en Fix 3: {e}")
        results.append(("Fix 3: Task Persistence", False))
    
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    total_passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {total_passed}/{len(results)} tests pasados")
    
    if total_passed == len(results):
        print("\n🎉 ¡TODOS LOS FIXES FUNCIONAN CORRECTAMENTE!")
    else:
        print("\n⚠️ Algunos fixes necesitan revisión")
