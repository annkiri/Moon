import shutil
import subprocess
import sys
from pathlib import Path


def open_database(db_name: str = "finance.db"):
    db_path = Path.cwd() / db_name

    if not db_path.exists():
        print(f"\033[0;31m[ERROR] Database not found: {db_name}\033[0m")
        return

    print(f"[INFO] Opening '{db_name}'...")
    print("-" * 40)

    # OPCIÓN A: NPX (Outerbase Studio) - TU PREFERENCIA
    # Requiere tener Node.js instalado. Es la opción más moderna y visual.
    if shutil.which("npx"):
        print("   [MODE] Using 'npx @outerbase/studio' (Zero-Install)")
        print("   [TIP]  First run might take a moment to download cached binaries.")
        try:
            # Lanza Outerbase Studio apuntando a tu archivo local
            subprocess.run(["npx", "@outerbase/studio", str(db_path)], check=True)
            return
        except subprocess.CalledProcessError:
            print("\033[0;31m   [ERR] npx failed. Trying fallback...\033[0m")
        except KeyboardInterrupt:
            return

    # OPCIÓN B: PIPX (Python Zero-Install)
    # Equivalente a npx pero nativo de Python. No ensucia requirements.txt
    if shutil.which("pipx"):
        print("   [MODE] Using 'pipx run sqlite-web' (Zero-Install)")
        try:
            subprocess.run(
                ["pipx", "run", "sqlite-web", str(db_path), "--open"], check=True
            )
            return
        except Exception:
            pass

    # OPCIÓN C: FALLBACK (Instalación Local)
    # Si no hay npx ni pipx, usamos la librería local del venv (si existe)
    if shutil.which("sqlite_web"):
        print("   [MODE] Using local 'sqlite-web'")
        subprocess.run(["sqlite_web", str(db_path), "--open"])
        return

    # SI TODO FALLA
    print("\033[0;33m[WARN] No database viewer found.\033[0m")
    print("   To use the 'npx' method you recalled, you need Node.js:")
    print("   👉 brew install node")
    print("\n   Or use the local Python fallback:")
    print("   👉 pip install sqlite-web")


if __name__ == "__main__":
    target_db = sys.argv[1] if len(sys.argv) > 1 else "finance.db"
    open_database(target_db)
