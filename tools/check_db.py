import sqlite3

import pandas as pd

# Conexión directa a la base de datos
conn = sqlite3.connect("finance.db")

print("--- 💰 GASTOS (Transactions) ---")
try:
    df_tx = pd.read_sql_query(
        "SELECT * FROM transactions ORDER BY id DESC LIMIT 5", conn
    )
    print(df_tx.to_markdown(index=False))
except Exception as e:
    print("Tabla vacía o error:", e)

print("\n--- 📝 NOTAS (Notes) ---")
try:
    df_notes = pd.read_sql_query("SELECT * FROM notes ORDER BY id DESC LIMIT 5", conn)
    print(df_notes.to_markdown(index=False))
except Exception as e:
    print("Tabla vacía o error:", e)

print("\n--- ✅ TAREAS (Tasks) ---")
try:
    df_tasks = pd.read_sql_query("SELECT * FROM tasks ORDER BY id DESC LIMIT 5", conn)
    print(df_tasks.to_markdown(index=False))
except Exception as e:
    print("Tabla vacía o error:", e)

conn.close()
