# ADB Toolkit API Reference

All endpoints require a connected ADB device.

## Authentication

None — runs locally on your machine.

## Devices

### List Devices
```
GET /api/devices
```

**Response:**
```json
[
  {"serial": "emulator-5554", "model": "Android Emulator", "android": "12"},
  {"serial": "192.168.1.100:5555", "model": "OnePlus 9", "android": "13"}
]
```

---

## Device Info

### Get Device Information
```
GET /api/device/<serial>/info
```

**Response:**
```json
{
  "model": "Pixel 6",
  "android": "13",
  "api": 33,
  "build": "TQ3A.210705.001",
  "storage": {"total": "128GB", "free": "45GB"},
  "battery": {"level": 87, "temp": 35}
}
```

---

## Apps

### List Installed Packages
```
GET /api/device/<serial>/packages?type=user|system|all
```

**Query Parameters:**
- `type` — `user` (default), `system`, or `all`

**Response:**
```json
[
  {"package": "com.example.app", "label": "Example App", "version": "1.0.0"},
  {"package": "com.another.app", "label": "Another", "version": "2.1"}
]
```

### Install APK
```
POST /api/device/<serial>/install
Content-Type: multipart/form-data

apk_file: <binary APK file>
```

### Uninstall Package
```
POST /api/device/<serial>/uninstall
Content-Type: application/json

{"package": "com.example.app"}
```

### Clear App Data
```
POST /api/device/<serial>/clear
Content-Type: application/json

{"package": "com.example.app"}
```

---

## Input & Control

### Tap Screen
```
POST /api/device/<serial>/tap
Content-Type: application/json

{"x": 540, "y": 960}
```

### Swipe Screen
```
POST /api/device/<serial>/swipe
Content-Type: application/json

{"x1": 540, "y1": 1500, "x2": 540, "y2": 500, "duration": 300}
```

### Type Text
```
POST /api/device/<serial>/text
Content-Type: application/json

{"input": "hello world"}
```

### Send Key Event
```
POST /api/device/<serial>/key
Content-Type: application/json

{"code": 4}  // 4 = BACK button
```

---

## Files

### List Directory
```
GET /api/device/<serial>/files?path=/sdcard/DCIM
```

### Push File
```
POST /api/device/<serial>/push
Content-Type: multipart/form-data

file: <binary data>
path: /sdcard/file.txt
```

### Pull File
```
GET /api/device/<serial>/pull?path=/sdcard/file.txt
```

---

## Logcat

### Stream Logcat
```
GET /api/device/<serial>/logcat?filter=*:V
```

**Note:** WebSocket recommended for streaming. Falls back to chunked HTTP.

---

## Error Responses

### Device Not Found
```json
{"error": "device_not_found", "status": 404}
```

### ADB Command Failed
```json
{"error": "command_failed", "details": "...", "status": 500}
```
