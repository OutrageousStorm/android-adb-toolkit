#!/usr/bin/env python3
"""
server.py -- Lightweight Flask server for the web-ui.html dashboard
Usage: python3 server.py
Then open: http://localhost:5000
Requires: pip install flask
"""
from flask import Flask, jsonify, request
import subprocess, json

app = Flask(__name__)

def run_adb(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    with open('web-ui.html') as f:
        return f.read()

@app.route('/api/adb', methods=['POST'])
def adb_command():
    data = request.json
    cmd = data.get('cmd', '').strip()
    if not cmd:
        return jsonify({'success': False, 'error': 'No command'})
    
    # Whitelist for safety
    allowed = ['adb', 'getprop', 'settings', 'dumpsys', 'pm', 'input', 'shell', 'wm']
    if not any(a in cmd for a in allowed):
        return jsonify({'success': False, 'error': 'Command not allowed'})
    
    result = run_adb(cmd)
    return jsonify({
        'success': len(result) > 0,
        'result': result,
        'cmd': cmd
    })

if __name__ == '__main__':
    print("\n🖥️  ADB Toolkit Server")
    print("Open: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(debug=False, host='127.0.0.1', port=5000)
