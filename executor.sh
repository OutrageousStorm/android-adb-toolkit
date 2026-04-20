#!/bin/bash
# executor.sh -- Interactive ADB shell with history
set -e
HISTORY_FILE="$HOME/.adb_history"
echo "ADB Shell — type 'help' for commands"

while true; do
    read -p "adb> " cmd
    [[ -z "$cmd" ]] && continue
    [[ "$cmd" == "help" ]] && { echo "Commands: help, history, exit"; continue; }
    [[ "$cmd" == "history" ]] && { tail -20 "$HISTORY_FILE" 2>/dev/null || echo "(empty)"; continue; }
    [[ "$cmd" == "exit" ]] && break
    echo "$cmd" >> "$HISTORY_FILE"
    adb shell "$cmd" 2>&1 | head -20
done
