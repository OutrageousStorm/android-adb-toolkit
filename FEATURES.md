# ADB Toolkit Features

## Web UI Dashboard (HTML/JS)
- Real-time device info (CPU, RAM, battery, network)
- Package manager — install/uninstall/clear
- File browser — push/pull files
- Screen control — brightness, display density, orientation
- Quick toggle buttons — WiFi, Bluetooth, airplane mode, doze
- App launcher with search
- Screenshot & screen record preview

## ADB Server Requirements
```bash
# Linux/Mac: adb daemon runs automatically
# Windows: adb server included in SDK Platform Tools

# Verify server is running:
adb start-server
adb devices  # should show connected device
```

## Endpoints (via adb forward)
```
GET  /device/info
GET  /packages/list
POST /packages/install
POST /packages/uninstall
GET  /files/list?path=/sdcard
GET  /settings/get?key=screen_brightness
POST /settings/put?key=screen_brightness&value=200
GET  /screenshot
POST /screen/tap?x=540&y=960
POST /screen/text?input=hello
```

## Usage
```bash
# Start ADB server
adb start-server

# Forward web UI
adb forward tcp:8080 tcp:8080

# Open browser
http://localhost:8080
```
