import os
import sqlite3
from datetime import datetime

# 1. Ubicar la base de datos
db_path = "finance.db"
print(f"🔍 BUSCANDO EN: {os.path.abspath(db_path)}")

if not os.path.exists(db_path):
    print("❌ ERROR CRÍTICO: El archivo finance.db NO EXISTE en esta carpeta.")
    exit()

# 2. Conectar crudo (Sin SQLAlchemy)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 3. Listar tablas
print("\n--- 📂 TABLAS ENCONTRADAS ---")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for t in tables:
        print(f" - {t[0]}")
except Exception as e:
    print(f"Error listando tablas: {e}")

# 4. Investigar la tabla TRANSACTIONS
print("\n--- 💰 CONTENIDO DE 'TRANSACTIONS' (Últimos 5) ---")
try:
    # Intenta con 'transactions' (plural) que es lo estándar
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    if not rows:
        print("⚠️  LA TABLA ESTÁ VACÍA (0 filas).")
    else:
        for r in rows:
            print(f" ✅ Gasto encontrado: {r}")
except sqlite3.OperationalError:
    print(
        "❌ LA TABLA 'transactions' NO EXISTE. ¿Quizás se llama 'transaction' (singular)?"
    )
    try:
        cursor.execute(
            "SELECT * FROM transaction_model ORDER BY id DESC LIMIT 5"
        )  # Intento alternativo
        rows = cursor.fetchall()
        for r in rows:
            print(f" ✅ Gasto encontrado (en transaction_model): {r}")
    except:
        pass

# 5. Investigar Tareas y Notas (Para comparar)
print("\n--- ✅ CONTENIDO DE 'TASKS' ---")
try:
    cursor.execute("SELECT count(*) FROM tasks")
    print(f" Total Tareas: {cursor.fetchone()[0]}")
except:
    print("Error leyendo tasks")

print("\n--- 📝 CONTENIDO DE 'NOTES' ---")
try:
    cursor.execute("SELECT count(*) FROM notes")
    print(f" Total Notas: {cursor.fetchone()[0]}")
except:
    print("Error leyendo notes")

conn.close()
