import os
from pathlib import Path


def generate_project_tree(
    start_path: Path, output_filename: str = "project_structure.txt"
):
    # Carpetas a ignorar en el mapa
    ignore_set = {
        ".venv",
        "venv",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist",
        ".kedro",
        ".ipynb_checkpoints",
        ".DS_Store",
        "node_modules",
    }

    output_path = start_path / output_filename

    with open(output_path, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(start_path):
            dirs[:] = [d for d in dirs if d not in ignore_set]

            rel_path = os.path.relpath(root, start_path)
            if rel_path == ".":
                level = 0
            else:
                level = rel_path.count(os.sep) + 1

            indent = " " * 4 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")

            subindent = " " * 4 * (level + 1)
            for file in files:
                if file not in [output_filename, ".DS_Store"]:
                    f.write(f"{subindent}{file}\n")

    print(f"[SUCCESS] Tree generated: {output_filename}")


if __name__ == "__main__":
    generate_project_tree(Path.cwd())
