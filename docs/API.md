# ADB Toolkit API Reference

HTTP endpoints exposed by the Node.js server.

## Device Info

```
GET /api/device/info
→ { model, android_version, storage, battery, serial }

GET /api/device/apps
→ { installed: [packages], count: N }

GET /api/device/settings?key=<setting>
→ { value: string }
```

## App Management

```
POST /api/app/install
Body: { apk_url: string }

POST /api/app/uninstall
Body: { package: string }

GET /api/app/permissions?package=<pkg>
→ { granted: [], denied: [] }
```

## Backup/Restore

```
POST /api/backup/start
→ { job_id: string }

GET /api/backup/status?job_id=<id>
→ { progress: 0-100, status: "running|complete|error" }
```

## WebSocket Events

```
ws://localhost:3000/stream

Events:
- "notification" {pkg, title, text}
- "logcat" {tag, message}
- "battery" {level, status}
```
