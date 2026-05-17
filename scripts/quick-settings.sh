#!/bin/bash
# quick-settings.sh — Fast ADB settings tweaks
# Usage: ./quick-settings.sh [option]
# Examples:
#   ./quick-settings.sh show-fps
#   ./quick-settings.sh 120hz
#   ./quick-settings.sh status-bar-clock

set -e

adb() { command adb shell "$@"; }

case "${1:-menu}" in
  show-fps)
    adb settings put developer show_fps_counter 1
    echo "✓ FPS counter enabled"
    ;;
  hide-fps)
    adb settings put developer show_fps_counter 0
    echo "✓ FPS counter disabled"
    ;;
  120hz)
    adb settings put secure min_refresh_rate 120
    adb settings put secure peak_refresh_rate 120
    echo "✓ Peak refresh rate: 120Hz"
    ;;
  60hz)
    adb settings put secure min_refresh_rate 60
    adb settings put secure peak_refresh_rate 60
    echo "✓ Peak refresh rate: 60Hz"
    ;;
  status-bar-clock)
    adb settings put secure status_bar_show_clock 1
    echo "✓ Status bar clock enabled"
    ;;
  no-status-clock)
    adb settings put secure status_bar_show_clock 0
    echo "✓ Status bar clock disabled"
    ;;
  animations)
    adb settings put global window_animation_scale 1.0
    adb settings put global transition_animation_scale 1.0
    adb settings put global animator_duration_scale 1.0
    echo "✓ Animations: normal"
    ;;
  fast-animations)
    adb settings put global window_animation_scale 0.5
    adb settings put global transition_animation_scale 0.5
    adb settings put global animator_duration_scale 0.5
    echo "✓ Animations: 50% speed"
    ;;
  no-animations)
    adb settings put global window_animation_scale 0
    adb settings put global transition_animation_scale 0
    adb settings put global animator_duration_scale 0
    echo "✓ Animations: disabled"
    ;;
  dev-mode-on)
    adb settings put global development_settings_enabled 1
    adb settings put global secure_adb_enabled 1
    echo "✓ Developer options enabled + USB debugging"
    ;;
  logcat-brief)
    adb logcat -v brief | head -50
    ;;
  logcat-stop)
    adb logcat -c
    echo "✓ Logcat buffer cleared"
    ;;
  *)
    echo "Quick Settings Manager"
    echo "Usage: $0 [option]"
    echo ""
    echo "Display:"
    echo "  show-fps / hide-fps"
    echo "  120hz / 60hz"
    echo "  status-bar-clock / no-status-clock"
    echo ""
    echo "Performance:"
    echo "  animations / fast-animations / no-animations"
    echo ""
    echo "Developer:"
    echo "  dev-mode-on"
    echo "  logcat-brief / logcat-stop"
    ;;
esac
