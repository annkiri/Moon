#!/bin/bash
# --- PROJECT ALIASES ---

bundle() {
    python tools/bundle_context.py "$@"
}

tree() {
    python tools/generate_tree.py
}

db() {
    python tools/open_db.py "$@"
}

run() {
    # Delega la ejecución a Python
    python tools/run_app.py "$@"
}

diff() {
    # Copia solo lo que has modificado
    python tools/bundle_diff.py
}

echo "   [INFO] Aliases ready: 'bundle', 'tree', 'db', 'run', 'diff' "
