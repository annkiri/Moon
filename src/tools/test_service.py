import sys
import os
import json

# Ajuste de path para importar módulos internos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv
from src.modules.finance.service import FinanceService

# Cargar entorno
load_dotenv()

def test_finance_service():
    print("--- TEST DE INTEGRACIÓN: FINANCE SERVICE ---")
    
    # 1. Instanciar el servicio (La 'Herramienta Fría')
    try:
        service = FinanceService()
        print("✅ Servicio inicializado correctamente.")
    except Exception as e:
        print(f"❌ Error al iniciar servicio: {e}")
        return

    # 2. Definir caso de prueba complejo
    # Usamos un caso con moneda implícita y categoría que requiere inferencia
    text_input = "Pagué 120 cocos por la mensualidad del gym"
    print(f"\n📝 Input: '{text_input}'")

    # 3. Ejecutar extracción
    try:
        print("⏳ Procesando con Llama 3.3...")
        transaction = service.extract_transaction_data(text_input)
        
        # 4. Mostrar resultado estructurado
        print("\n✅ RESULTADO OBTENIDO (Objeto Transaction):")
        print(json.dumps(transaction.model_dump(), indent=2))
        
        # Validaciones lógicas rápidas para el test
        if transaction.currency == "USD" and "gym" in transaction.category.lower():
            print("\n🌟 PRUEBA SUPERADA: Inferencia de moneda ('cocos'->USD) y categoría correcta.")
        else:
            print("\n⚠️ ALERTA: La inferencia no fue exacta, revisar lógica.")
            
    except Exception as e:
        print(f"\n❌ ERROR EN EJECUCIÓN: {e}")

if __name__ == "__main__":
    test_finance_service()