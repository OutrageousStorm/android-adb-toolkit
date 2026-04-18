#!/bin/bash
# bulk_ops.sh -- Perform operations on groups of apps
# Usage: ./bulk_ops.sh disable com.facebook.katana com.instagram.android
#        ./bulk_ops.sh enable --all-social

set -e

OP="$1"
shift

SOCIAL_APPS=(
  "com.facebook.katana"
  "com.instagram.android"
  "com.twitter.android"
  "com.snapchat.android"
  "com.linkedin.android"
)

if [[ "$1" == "--all-social" ]]; then
  TARGETS=("${SOCIAL_APPS[@]}")
else
  TARGETS=("$@")
fi

case "$OP" in
  disable)
    for pkg in "${TARGETS[@]}"; do
      echo "Disabling $pkg..."
      adb shell pm disable-user --user 0 "$pkg" 2>/dev/null && echo "  ✓" || echo "  ✗"
    done
    ;;
  enable)
    for pkg in "${TARGETS[@]}"; do
      echo "Enabling $pkg..."
      adb shell pm enable "$pkg" 2>/dev/null && echo "  ✓" || echo "  ✗"
    done
    ;;
  clear)
    for pkg in "${TARGETS[@]}"; do
      echo "Clearing $pkg..."
      adb shell pm clear "$pkg" 2>/dev/null && echo "  ✓" || echo "  ✗"
    done
    ;;
  uninstall)
    for pkg in "${TARGETS[@]}"; do
      echo "Uninstalling $pkg..."
      adb shell pm uninstall -k --user 0 "$pkg" 2>/dev/null && echo "  ✓" || echo "  ✗"
    done
    ;;
  *)
    echo "Usage: $0 {disable|enable|clear|uninstall} [--all-social] [packages...]"
    exit 1
esac

echo "Done."
