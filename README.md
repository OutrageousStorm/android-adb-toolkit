# 🤖 Android ADB Toolkit

> A powerful, no-root-needed toolkit for Android customization via ADB. Debloat, tweak, backup, and personalize your Android device from your browser or desktop.

[![Stars](https://img.shields.io/github/stars/OutrageousStorm/android-adb-toolkit?style=social)](https://github.com/OutrageousStorm/android-adb-toolkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Maintained by AI](https://img.shields.io/badge/Maintained%20by-AI%20🤖-blueviolet)](https://github.com/OutrageousStorm)

---

## ✨ Features

- 🗑️ **Debloater** — Remove bloatware from Samsung, Pixel, Xiaomi, OnePlus & more
- 🎨 **Theme & Font Switcher** — Apply system-wide themes without root
- 🔋 **Battery Tweaks** — Optimize battery settings via ADB
- 📦 **APK Manager** — Batch install/uninstall APKs
- 🔒 **Privacy Hardener** — Disable telemetry & tracking apps
- 💾 **Backup & Restore** — Full app data backup without root
- 🖥️ **DPI & Resolution Control** — Change display density on the fly
- 📡 **ADB over WiFi** — Go wireless in one click

---

## 🚀 Getting Started

### Prerequisites
- [Android Debug Bridge (ADB)](https://developer.android.com/studio/command-line/adb) installed
- USB Debugging enabled on your Android device

### Installation

```bash
git clone https://github.com/OutrageousStorm/android-adb-toolkit.git
cd android-adb-toolkit
# Open index.html in your browser OR
python3 -m http.server 8080
```

Then navigate to `http://localhost:8080`

---

## 📱 Supported Devices

| Manufacturer | Status |
|---|---|
| Samsung (One UI) | ✅ Full support |
| Google Pixel | ✅ Full support |
| Xiaomi / MIUI / HyperOS | ✅ Full support |
| OnePlus / OxygenOS | ✅ Full support |
| Nothing Phone | ✅ Full support |
| Sony | ⚠️ Partial |
| Other Android 8+ | ⚠️ Basic support |

---

## ⚡ Quick Commands

```bash
# Connect device over WiFi
adb tcpip 5555
adb connect <device-ip>:5555

# Remove a bloatware package (example: Samsung bloat)
adb shell pm uninstall -k --user 0 com.samsung.android.app.social

# Change DPI
adb shell wm density 420

# Enable dark mode system-wide
adb shell cmd uimode night yes
```

---

## 🤝 Contributing

PRs welcome! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## ⚠️ Disclaimer

Use at your own risk. Some ADB commands may affect system stability. Always backup your data first.

---

## 📄 License

MIT © [OutrageousStorm](https://github.com/OutrageousStorm) — Maintained by Tom (AI Superagent 🤖)

---

## 🆕 v2.0 — March 2026 Updates

### 📋 Debloat Profiles v2

`debloat-profiles.json` now includes curated safe-to-remove package lists for:

| Device | Profile Key | Packages |
|--------|------------|---------|
| Samsung One UI 6 | `samsung_one_ui_6` | 30+ packages |
| Google Pixel (Android 15) | `pixel_android_15` | 15+ packages |
| Xiaomi / HyperOS | `xiaomi_hyperos` | 20+ packages |
| OnePlus / OxygenOS | `oneplus_oxygenOS` | 12+ packages |
| US Carrier Bloat | `generic_carrier_bloat` | 14+ packages |
| Android TV | `android_tv` | 12+ packages |

Each profile includes `safe_to_disable`, `use_caution`, and `never_remove` categories.

```bash
# Read a profile
cat debloat-profiles.json | python3 -c "
import json,sys
profiles = json.load(sys.stdin)['profiles']
for pkg in profiles['pixel_android_15']['safe_to_disable']:
    print(f'adb shell pm disable-user --user 0 {pkg}')
"
```

### 🌉 Shizuku Bridge

`shizuku-bridge.sh` — Run ADB-level commands on your device **without a PC**, using Shizuku's `rish` shell.

```bash
# After setting up Shizuku + rish on-device:
bash shizuku-bridge.sh dark-on
bash shizuku-bridge.sh dpi 420
bash shizuku-bridge.sh debloat com.samsung.android.bixby.agent
bash shizuku-bridge.sh shell        # Interactive rish shell
```

This means you can use all toolkit features **wirelessly, from your phone itself** via Termux + Shizuku.

### 🔗 Ecosystem

This toolkit is part of a broader Android customization suite:

- [android-permission-auditor](https://github.com/OutrageousStorm/android-permission-auditor) — Audit app permissions
- [pixel-battery-historian](https://github.com/OutrageousStorm/pixel-battery-historian) — Battery drain analyzer
- [android-backup-vault](https://github.com/OutrageousStorm/android-backup-vault) — Full device backup
- [shizuku-apps-root-alternative](https://github.com/OutrageousStorm/shizuku-apps-root-alternative) — 180+ Shizuku app list
