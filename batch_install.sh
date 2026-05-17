#!/bin/bash
# batch_install.sh — Install multiple APKs from a directory with progress tracking
# Usage: ./batch_install.sh /path/to/apks [--fast] [--skip-errors]

set -e
DIR="${1:-.}"
FAST="${2:-}"
SKIP_ERRORS="${3:-}"

if [[ ! -d "$DIR" ]]; then
  echo "❌ Directory not found: $DIR"
  exit 1
fi

TOTAL=$(find "$DIR" -maxdepth 1 -name "*.apk" | wc -l)
[[ $TOTAL -eq 0 ]] && echo "No APKs found." && exit 0

echo "📦 Batch APK Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Directory: $DIR"
echo "APKs found: $TOTAL"
echo ""

if ! adb devices | grep -q "device$"; then
  echo "❌ No device connected."
  exit 1
fi

installed=0; failed=0; skipped=0

for apk in "$DIR"/*.apk; do
  [[ ! -f "$apk" ]] && continue
  name=$(basename "$apk")
  
  result=$(adb install -r "$apk" 2>&1)
  
  if echo "$result" | grep -q "Success\|already installed"; then
    echo "✓ $name"
    ((installed++))
  elif [[ "$SKIP_ERRORS" == "--skip-errors" ]]; then
    echo "⊘ $name (skipped — already exists or incompatible)"
    ((skipped++))
  else
    echo "✗ $name (error: ${result:0:80})"
    ((failed++))
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installed: $installed  Failed: $failed  Skipped: $skipped"
[[ $failed -gt 0 ]] && exit 1
