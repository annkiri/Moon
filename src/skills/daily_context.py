"""
Sistema de Contexto Diario Inteligente para Moon AI v3.1

FILOSOFÍA:
- Guardar RESÚMENES de interacciones, no transcripciones completas
- Límite de 50KB por archivo (~500 interacciones aprox)
- Rotación automática semanal
- Solo contenido relevante para contexto conversacional

¿QUÉ SE GUARDA?
✅ Temas discutidos (keywords)
✅ Decisiones tomadas
✅ Consultas importantes del usuario
❌ NO confirmaciones simples ("ok", "gracias")
❌ NO transacciones individuales (ya están en SQLite)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

CONTEXT_DIR = Path("./daily_context")
CONTEXT_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 50 * 1024  # 50KB
RETENTION_DAYS = 7


def get_today_file() -> Path:
    """Retorna la ruta del archivo de hoy (ej: 2026-01-30.jsonl)"""
    today = datetime.now().strftime("%Y-%m-%d")
    return CONTEXT_DIR / f"{today}.jsonl"


def should_save_interaction(user_msg: str, bot_msg: str) -> bool:
    """
    Decide si vale la pena guardar esta interacción.
    
    SKIP si:
    - Usuario solo confirma ("ok", "gracias", "vale")
    - Mondri solo confirma guardado de transacción
    - Mensajes muy cortos sin contexto
    """
    # Mensajes ignorables del usuario
    skip_patterns = ["ok", "gracias", "vale", "listo", "perfecto", "entendido"]
    if user_msg.lower().strip() in skip_patterns:
        return False
    
    # Solo confirmaciones de guardado (no aportan contexto)
    if "guardado" in bot_msg.lower() and len(bot_msg) < 100:
        return False
    
    # Mensajes muy cortos
    if len(user_msg) < 10 and len(bot_msg) < 50:
        return False
    
    return True


def append_to_daily(user_msg: str, bot_msg: str, intent: Optional[str] = None):
    """
    Añade una interacción al archivo del día (formato JSONL).
    
    Estructura:
    {
        "timestamp": "21:15",
        "user": "¿Gasto mucho en comida?",
        "bot": "Resumen de respuesta...",
        "intent": "chat",
        "keywords": ["comida", "gasto", "análisis"]
    }
    """
    # Evaluar si vale la pena guardar
    if not should_save_interaction(user_msg, bot_msg):
        print("[DAILY] Interaccion trivial, no guardada")
        return
    
    file_path = get_today_file()
    
    # Verificar tamaño del archivo
    if file_path.exists() and file_path.stat().st_size > MAX_FILE_SIZE:
        print(f"[WARN] Archivo de hoy excede {MAX_FILE_SIZE} bytes, rotando...")
        # Renombrar con timestamp para mantener múltiples archivos del mismo día
        timestamp = datetime.now().strftime("%H%M")
        backup_path = CONTEXT_DIR / f"{file_path.stem}-{timestamp}.jsonl"
        file_path.rename(backup_path)
    
    # Extraer keywords (primeras 5 palabras significativas)
    keywords = extract_keywords(user_msg + " " + bot_msg)
    
    entry = {
        "timestamp": datetime.now().strftime("%H:%M"),
        "user": truncate(user_msg, 200),  # Máximo 200 chars
        "bot": truncate(bot_msg, 300),    # Máximo 300 chars
        "intent": intent,
        "keywords": keywords[:5]  # Máximo 5 keywords
    }
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"[DAILY] Guardado: {entry['keywords']}")


def extract_keywords(text: str) -> list[str]:
    """Extrae palabras clave del texto (simple filter de stopwords)"""
    stopwords = {
        "el", "la", "de", "que", "y", "a", "en", "un", "ser", "se", "no", "haber",
        "por", "con", "su", "para", "como", "estar", "tener", "le", "lo", "todo",
        "pero", "más", "hacer", "o", "poder", "decir", "este", "ir", "otro", "ese",
        "ok", "gracias", "vale", "hola", "hi", "hey", "buenos", "dias"
    }
    
    words = text.lower().split()
    keywords = [w.strip(".,!?") for w in words if len(w) > 3 and w not in stopwords]
    return list(dict.fromkeys(keywords))  # Unique, preserving order


def truncate(text: str, max_len: int) -> str:
    """Trunca texto si excede max_len"""
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."


def read_daily_context(max_entries: int = 20) -> str:
    """
    Lee el contexto de hoy (últimas N interacciones).
    
    Retorna formato legible para el LLM:
    ---
    [14:30] User: ¿Gasto mucho en comida?
    Bot: Según tus datos...
    [15:45] User: Recuérdame llamar a mamá
    Bot: Agendado para mañana...
    ---
    """
    file_path = get_today_file()
    if not file_path.exists():
        return ""
    
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    # Últimas N entradas
    recent = entries[-max_entries:]
    
    if not recent:
        return ""
    
    # Formatear para el LLM
    formatted = []
    for entry in recent:
        formatted.append(f"[{entry['timestamp']}] User: {entry['user']}")
        formatted.append(f"Bot: {entry['bot']}")
    
    return "\n".join(formatted)


def cleanup_old_files():
    """
    Elimina archivos de más de RETENTION_DAYS días.
    Llamar en startup de la app.
    """
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    
    for file in CONTEXT_DIR.glob("*.jsonl"):
        # Extraer fecha del nombre (2026-01-30.jsonl)
        try:
            date_str = file.stem.split("-")[0:3]  # ['2026', '01', '30']
            file_date = datetime.strptime("-".join(date_str), "%Y-%m-%d")
            
            if file_date < cutoff:
                print(f"[DAILY] Eliminando archivo antiguo: {file.name}")
                file.unlink()
        except (ValueError, IndexError):
            # Formato inesperado, skip
            continue


# --- INICIALIZACIÓN AL IMPORTAR ---
# Limpiar archivos viejos al cargar el módulo
cleanup_old_files()
