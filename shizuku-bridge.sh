#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  shizuku-bridge.sh
#  Use Shizuku's rish shell to run ADB-level commands
#  directly ON the device — no PC required after setup.
#
#  Requires: Shizuku installed + rish configured
#  Setup: https://github.com/RikkaApps/Shizuku-API/blob/master/rish/README.md
# ═══════════════════════════════════════════════════════════

BOLD='\033[1m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'

RISH_PATH="${RISH_PATH:-/data/user_de/0/moe.shizuku.privileged.api/rish}"

has_rish() {
  adb shell "test -f $RISH_PATH && echo yes" 2>/dev/null | grep -q yes
}

rish_run() {
  local cmd="$1"
  adb shell "$RISH_PATH -c '$cmd'" 2>/dev/null
}

echo -e "${BOLD}🌉 Shizuku Bridge${NC} — Run ADB commands on-device via rish"
echo ""

if ! has_rish; then
  echo -e "${YELLOW}⚠ rish not found at $RISH_PATH${NC}"
  echo -e "  Setup guide: https://github.com/RikkaApps/Shizuku-API/blob/master/rish/README.md"
  echo -e "  Or set RISH_PATH env var to your rish location"
  exit 1
fi

echo -e "${GREEN}✓ rish detected${NC}"

case "${1:-menu}" in
  dark-on)
    rish_run "cmd uimode night yes"
    echo -e "${GREEN}✓ Dark mode enabled${NC}"
    ;;
  dark-off)
    rish_run "cmd uimode night no"
    echo -e "${GREEN}✓ Dark mode disabled${NC}"
    ;;
  dpi)
    dpi="${2:-420}"
    rish_run "wm density $dpi"
    echo -e "${GREEN}✓ DPI set to $dpi${NC}"
    ;;
  debloat)
    pkg="${2:-}"
    if [[ -z "$pkg" ]]; then
      echo "Usage: $0 debloat com.package.name"
      exit 1
    fi
    rish_run "pm disable-user --user 0 $pkg"
    echo -e "${GREEN}✓ Disabled: $pkg${NC}"
    ;;
  grant)
    pkg="${2:-}"
    perm="${3:-android.permission.WRITE_SECURE_SETTINGS}"
    rish_run "pm grant $pkg $perm"
    echo -e "${GREEN}✓ Granted $perm to $pkg${NC}"
    ;;
  shell)
    echo -e "${CYAN}Opening interactive rish shell...${NC}"
    adb shell "$RISH_PATH"
    ;;
  menu|*)
    echo "Commands:"
    echo "  $0 dark-on        Enable dark mode"
    echo "  $0 dark-off       Disable dark mode"
    echo "  $0 dpi [value]    Change DPI (default 420)"
    echo "  $0 debloat <pkg>  Disable a package"
    echo "  $0 grant <pkg> [perm]  Grant permission"
    echo "  $0 shell          Open interactive rish shell"
    ;;
esac
