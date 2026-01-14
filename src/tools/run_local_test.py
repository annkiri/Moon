import os
import sys
import json
from dotenv import load_dotenv
from groq import Groq

# Agregar src al path para permitir importaciones de módulos internos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.modules.finance.schemas import Transaction

# Cargar variables de entorno
load_dotenv()

def run_test():
    print("Iniciando prueba de concepto - Modulo de Finanzas...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERROR: Falta la variable GROQ_API_KEY en el archivo .env")
        return

    client = Groq(api_key=api_key)
    
    # 1. Entrada simulada
    input_text = "Acabo de gastar 25.50 en el Tambo comprando unas galletas y una gaseosa."
    print(f"Texto de entrada: '{input_text}'")

    # 2. Prompt del Sistema (Reglas de Negocio)
    # IMPORTANTE: Forzamos las claves en inglés para cumplir con schemas.py
    system_prompt = """
    Eres un asistente financiero. Extrae los detalles de la transacción en formato JSON estricto.
    
    Reglas de Extracción:
    - Moneda por defecto: PEN.
    - Fecha por defecto: 2026-01-14.
    - Categoría: Inferir inteligentemente (ej. 'Tambo' -> 'Antojos').
    
    ESQUEMA JSON OBLIGATORIO (Usa estas claves exactas):
    {
      "amount": <float>,
      "currency": <str>,
      "category": <str>,
      "merchant": <str>,
      "date": <YYYY-MM-DD>,
      "notes": <str>
    }
    """

    # 3. Inferencia con Llama 3.3
    try:
        print("Consultando a Llama 3.3 via Groq...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        result_content = completion.choices[0].message.content
        
        # 4. Validación con Pydantic
        transaction = Transaction.model_validate_json(result_content)
        
        print("\nEXITO. Datos validados:")
        print(json.dumps(transaction.model_dump(), indent=2))
        
    except Exception as e:
        print(f"\nFALLO: {e}")

if __name__ == "__main__":
    run_test()