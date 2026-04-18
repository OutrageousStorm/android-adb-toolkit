#!/usr/bin/env python3
"""
server.py -- Simple REST API for ADB commands
Expose device control via HTTP so web UI can talk to ADB backend
Usage: python3 server.py --port 5000
"""
from flask import Flask, request, jsonify
import subprocess, json

app = Flask(__name__)

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip(), r.returncode

@app.route('/api/device/info', methods=['GET'])
def device_info():
    """Get device model, Android version, storage"""
    return jsonify({
        'model': adb("getprop ro.product.model")[0],
        'android': adb("getprop ro.build.version.release")[0],
        'storage': adb("df -h /data | tail -1")[0],
    })

@app.route('/api/device/battery', methods=['GET'])
def battery():
    """Get battery status"""
    out = adb("dumpsys battery")[0]
    return jsonify({'raw': out})

@app.route('/api/apps/list', methods=['GET'])
def list_apps():
    """List installed packages"""
    out = adb("pm list packages -3")[0]
    apps = [l.split(":")[-1] for l in out.splitlines() if l.startswith("package:")]
    return jsonify({'apps': apps, 'count': len(apps)})

@app.route('/api/apps/install', methods=['POST'])
def install_app():
    """Install APK from path"""
    path = request.json.get('apk_path')
    out, code = adb(f"install {path}")
    return jsonify({'status': 'success' if code == 0 else 'failed', 'output': out})

@app.route('/api/settings/get', methods=['GET'])
def get_setting():
    """Get a system setting"""
    namespace = request.args.get('namespace', 'system')  # system, secure, global
    key = request.args.get('key')
    val = adb(f"settings get {namespace} {key}")[0]
    return jsonify({'key': key, 'value': val})

@app.route('/api/settings/set', methods=['POST'])
def set_setting():
    """Set a system setting"""
    data = request.json
    namespace = data.get('namespace', 'system')
    key = data.get('key')
    val = data.get('value')
    adb(f"settings put {namespace} {key} {val}")
    return jsonify({'status': 'ok'})

@app.route('/api/shell', methods=['POST'])
def shell():
    """Execute arbitrary shell command"""
    cmd = request.json.get('cmd')
    if not cmd:
        return jsonify({'error': 'no cmd'}), 400
    out, code = adb(cmd)
    return jsonify({'output': out, 'code': code})

if __name__ == "__main__":
    print("ADB REST API Server running on http://localhost:5000")
    app.run(debug=False, port=5000)
