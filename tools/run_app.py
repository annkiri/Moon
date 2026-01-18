import subprocess
import sys
from pathlib import Path


def run_streamlit_app():
    # 1. Definir la ruta del entry point (SSOT)
    root = Path.cwd()
    # Basado en tu estructura actual: src/interface/streamlit_app.py
    app_path = root / "src" / "interface" / "streamlit_app.py"

    # 2. Validar existencia
    if not app_path.exists():
        print(f"\033[0;31m[ERROR] App entry point not found.\033[0m")
        print(f"       Expected at: {app_path}")
        return

    # 3. Ejecutar Streamlit
    try:
        print(f"[INFO] Launching Moon AI from: {app_path.relative_to(root)}...")
        # Pasamos los argumentos extra (sys.argv[1:]) por si quieres agregar flags como --server.port 8502
        cmd = ["streamlit", "run", str(app_path)] + sys.argv[1:]

        # Ejecutamos el subproceso conectando la salida a la terminal actual
        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
    except subprocess.CalledProcessError:
        print("\033[0;31m[ERROR] Streamlit crashed.\033[0m")
    except FileNotFoundError:
        print("\033[0;31m[ERROR] 'streamlit' command not found.\033[0m")
        print("       Did you run 'pip install streamlit' in your .venv?")


if __name__ == "__main__":
    run_streamlit_app()
