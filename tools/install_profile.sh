#!/bin/bash
# --- PROFILE INSTALLER (SMART ACTIVATOR) ---

PROFILE_FILE="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ] || [[ "$SHELL" == *"zsh"* ]]; then
    PROFILE_FILE="$HOME/.zshrc"
fi

read -r -d '' FUNC_BLOCK << EOM

# --- DEV TOOLS ACTIVATOR ---
on() {
    # 1. VENV ACTIVATION
    if [ -f ".venv/bin/activate" ]; then
        source ".venv/bin/activate"
        echo -e "\033[0;32m[✔] Virtual Environment activated (.venv)\033[0m"
    elif [ -f "../.venv/bin/activate" ]; then
        source "../.venv/bin/activate"
        echo -e "\033[0;32m[✔] Virtual Environment activated (../.venv)\033[0m"
    else
        echo -e "\033[0;33m[!] No .venv found here.\033[0m"
    fi

    # 2. TOOLS LOADER
    if [ -f "tools/load_aliases.sh" ]; then
        source "tools/load_aliases.sh"
        echo -e "\033[0;36m[✔] Local tools loaded\033[0m"
    fi
}
# ---------------------------
EOM

if grep -q "DEV TOOLS ACTIVATOR" "$PROFILE_FILE"; then
    echo "[WARN] 'on' command already exists."
else
    echo "$FUNC_BLOCK" >> "$PROFILE_FILE"
    echo "[SUCCESS] Installed in $PROFILE_FILE."
fi
