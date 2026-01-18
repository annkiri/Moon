import argparse
import subprocess
import sys
from pathlib import Path

import pyperclip


def get_changed_files():
    try:
        # 1. Archivos modificados (Tracked)
        modified = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"], text=True
        ).splitlines()

        # 2. Archivos nuevos (Untracked)
        untracked = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"], text=True
        ).splitlines()

        return set(modified + untracked)
    except subprocess.CalledProcessError:
        print("\033[0;31m[ERROR] Not a git repository or git error.\033[0m")
        return []


def main():
    print(f"[PROCESS] Detecting changes via Git...")
    changed_files = get_changed_files()

    if not changed_files:
        print("   [INFO] No changes detected (clean working tree).")
        return

    # Filtros de seguridad (Ignorar archivos de sistema/lock)
    ignore_ext = {".db", ".DS_Store", ".pyc", ".png", ".jpg"}
    files_to_bundle = [f for f in changed_files if Path(f).suffix not in ignore_ext]

    if not files_to_bundle:
        print("   [INFO] Changes detected but ignored (only binary/db files changed).")
        return

    # Reutilizamos tu lógica de bundle visual
    root = Path.cwd()
    buffer = []

    for fname in files_to_bundle:
        path = root / fname
        if path.exists() and path.is_file():
            try:
                content = path.read_text(encoding="utf-8")
                entry = f"=== FILE (CHANGED): {fname} ===\n```\n{content}\n```\n"
                buffer.append(entry)
                print(f"   [ADD] {fname}")
            except Exception:
                print(f"   [SKIP] Binary or read error: {fname}")

    if buffer:
        final_text = "\n".join(buffer)
        pyperclip.copy(final_text)
        print("-" * 40)
        print(f"[SUCCESS] {len(buffer)} changed files copied to clipboard.")
    else:
        print("[WARN] No readable content found in changes.")


if __name__ == "__main__":
    main()
