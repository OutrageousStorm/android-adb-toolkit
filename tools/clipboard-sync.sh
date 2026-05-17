#!/bin/bash
# clipboard-sync.sh -- Sync device clipboard to PC and vice versa
# Usage: ./clipboard-sync.sh [pull|push|watch]

set -e

case "${1:-watch}" in
    pull)
        echo "📋 Pulling device clipboard..."
        adb shell "am broadcast -a clipper.get.RESULT -n org.openintents.action.PROCESS_TEXT"
        adb shell "cat /dev/clipboard" 2>/dev/null || adb shell "settings get secure clipboard" || echo "Clipboard sync requires ADB clipboard permissions"
        ;;
    push)
        text="${2:?Provide text to push: ./clipboard-sync.sh push \"text here\"}"
        echo "📋 Pushing to device clipboard: $text"
        adb shell "echo '$text' | xclip -selection clipboard" 2>/dev/null || \
        adb shell "input text '$text'" || \
        echo "Clipboard write failed. Requires xclip on device or ADB input."
        ;;
    watch)
        echo "👁️  Watching device clipboard (Ctrl+C to stop)"
        while true; do
            current=$(adb shell "getprop clipboard" 2>/dev/null || echo "")
            if [[ -n "$current" ]]; then
                echo "[$(date '+%H:%M:%S')] Device: $current"
            fi
            sleep 2
        done
        ;;
    *)
        echo "Usage: $0 [pull|push|watch]"
        echo "  pull — get device clipboard text"
        echo "  push TEXT — send TEXT to device clipboard"
        echo "  watch — monitor device clipboard changes"
        ;;
esac
