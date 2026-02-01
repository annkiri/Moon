"""
Script de Test End-to-End
Moon AI v3.1

Simula flujos completos y mide latencia.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from langchain_core.messages import HumanMessage
from src.core.graph import app

def test_fast_path():
    """Test del flujo rápido (finance)"""
    print("\n" + "="*60)
    print("🔵 TEST 1: FLUJO RÁPIDO (Finance)")
    print("="*60)
    
    user_input = "Gasté 35 soles en un taxi"
    messages = [HumanMessage(content=user_input)]
    
    start = time.time()
    result = app.invoke({"messages": messages})
    elapsed = time.time() - start
    
    print(f"Input: {user_input}")
    print(f"Latencia: {elapsed:.2f}s")
    print(f"Respuesta: {result['messages'][-1].content}")
    print(f"Debug: {result.get('debug_logs', [])}")
    
    if elapsed < 1.0:
        print("✅ PASS: Latencia <1s (flujo rápido)")
    else:
        print(f"⚠️ WARN: Latencia {elapsed:.2f}s (esperado <1s)")
    
    return elapsed

def test_contextual_path():
    """Test del flujo contextual (chat con memoria)"""
    print("\n" + "="*60)
    print("🟣 TEST 2: FLUJO CONTEXTUAL (Chat)")
    print("="*60)
    
    user_input = "¿Qué es la inteligencia artificial?"
    messages = [HumanMessage(content=user_input)]
    
    start = time.time()
    result = app.invoke({"messages": messages})
    elapsed = time.time() - start
    
    print(f"Input: {user_input}")
    print(f"Latencia: {elapsed:.2f}s")
    print(f"Respuesta: {result['messages'][-1].content[:200]}...")
    print(f"Debug: {result.get('debug_logs', [])}")
    
    if elapsed < 3.0:
        print("✅ PASS: Latencia aceptable para contexto completo")
    else:
        print(f"⚠️ WARN: Latencia alta {elapsed:.2f}s")
    
    return elapsed

def test_profile_path():
    """Test del flujo de perfil"""
    print("\n" + "="*60)
    print("🟠 TEST 3: FLUJO PERFIL (Profile)")
    print("="*60)
    
    user_input = "Me encanta el café con leche"
    messages = [HumanMessage(content=user_input)]
    
    start = time.time()
    result = app.invoke({"messages": messages})
    elapsed = time.time() - start
    
    print(f"Input: {user_input}")
    print(f"Latencia: {elapsed:.2f}s")
    print(f"Respuesta: {result['messages'][-1].content}")
    print(f"Debug: {result.get('debug_logs', [])}")
    
    return elapsed

if __name__ == "__main__":
    print("\n🧪 MOON AI v3.1 - END-TO-END TESTS")
    
    try:
        t1 = test_fast_path()
        time.sleep(1)  # Cooldown
        
        t2 = test_contextual_path()
        time.sleep(1)
        
        t3 = test_profile_path()
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE LATENCIAS")
        print("="*60)
        print(f"Finance (Fast): {t1:.2f}s")
        print(f"Chat (Context): {t2:.2f}s")
        print(f"Profile: {t3:.2f}s")
        print("\n✅ Tests completados. Revisa el archivo daily_context/[fecha].jsonl")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
