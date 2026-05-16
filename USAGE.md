# Android ADB Toolkit — Web UI Usage

## What it does

A single-page web tool for ADB power users. Point it at your device, run commands.

## Features

### Device Info Panel
Shows real-time:
- Battery level + temp
- CPU usage
- RAM usage
- Storage usage
- Network connectivity

### Command Executor
Pre-built buttons for:
- Debloat packages
- Grant/revoke permissions
- Take screenshots
- Record screen
- Control display (brightness, DPI)
- Manage apps

### Built-in debloat lists
One-click removal of:
- Samsung bloatware
- Google telemetry
- Facebook suite
- Ads/tracking frameworks

## Requirements
- ADB installed and in PATH
- Device connected via USB with USB debugging enabled
- Python 3.6+

## Running
```bash
python3 server.py
# Open http://localhost:8080 in your browser
```

## Security
- No data leaves your local machine
- ADB commands execute on your device only
- No external API calls
- Works offline
