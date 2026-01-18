import argparse
import sys
from pathlib import Path

import pyperclip


# Nota: La sintaxis "Path | None" requiere Python 3.10 o superior (Perfecto para tu 3.13)
def resolve_path(user_input: str, root_path: Path) -> Path | None:
    # 1. Búsqueda directa
    path = root_path / user_input
    if path.exists() and path.is_file():
        return path

    # 2. Búsqueda inteligente (Smart Search)
    # Ignora carpetas que no queremos leer nunca
    ignore_dirs = {
        ".venv",
        "venv",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".kedro",
        "build",
        "dist",
        "logs",
    }

    matches = []
    # Busca recursivamente ignorando basura
    for p in root_path.rglob(Path(user_input).name):
        if not any(part in ignore_dirs for part in p.parts):
            matches.append(p)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        # En caso de ambigüedad, prefiere la ruta más corta
        matches.sort(key=lambda x: len(x.parts))
        print(f"   [AMBIGUOUS] Found multiple '{user_input}'. Using: {matches[0]}")
        return matches[0]

    return None


def main():
    parser = argparse.ArgumentParser(description="Bundle code for AI Context")
    parser.add_argument("filenames", nargs="+", help="Files to bundle")
    args = parser.parse_args()

    root = Path.cwd()
    buffer = []
    total_chars = 0

    print(f"[PROCESS] Bundling files with Python {sys.version.split()[0]}...")

    for name in args.filenames:
        path = resolve_path(name, root)
        if not path:
            print(f"   [SKIP] Not found: {name}")
            continue

        try:
            content = path.read_text(encoding="utf-8")
            rel_path = path.relative_to(root).as_posix()

            # Formato claro para la IA
            entry = f"=== FILE: {rel_path} ===\n```\n{content}\n```\n"
            buffer.append(entry)
            total_chars += len(entry)
            print(f"   [OK] {rel_path}")

        except Exception as e:
            print(f"   [ERR] Error reading {name}: {e}")

    if not buffer:
        print("[FAIL] No content captured.")
        return

    # Estimación de Tokens (1 token ~= 4 caracteres)
    est_tokens = int(total_chars / 4)
    final_text = "\n".join(buffer)
    final_text += (
        f"\n=== METADATA ===\nFiles: {len(buffer)} | Est. Tokens: ~{est_tokens}"
    )

    try:
        pyperclip.copy(final_text)
        print("-" * 40)
        print(f"[SUCCESS] Copied to clipboard!")
        print(f"[METRICS] Est. Tokens: ~{est_tokens}")
    except Exception as e:
        print(f"[FATAL] Clipboard error: {e}")


if __name__ == "__main__":
    main()
