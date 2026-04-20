#!/usr/bin/env python3
"""
Lightweight ADB server wrapper — start/stop adb server with status
Usage: python3 server.py start|stop|status|restart
"""
import subprocess, sys, time

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip()

def get_status():
    ok, out = run("adb devices")
    if not ok:
        return "ERROR"
    lines = out.split('\n')[1:]
    devices = [l for l in lines if l.strip() and 'device' in l and 'offline' not in l]
    return f"RUNNING ({len(devices)} device{'s' if len(devices) != 1 else ''})"

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} start|stop|status|restart")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "start":
        print("Starting ADB server...")
        ok, _ = run("adb start-server")
        print("✓ Started" if ok else "✗ Failed")
    elif cmd == "stop":
        print("Stopping ADB server...")
        ok, _ = run("adb kill-server")
        print("✓ Stopped" if ok else "✗ Failed")
    elif cmd == "status":
        status = get_status()
        print(f"ADB: {status}")
    elif cmd == "restart":
        print("Restarting ADB...")
        run("adb kill-server")
        time.sleep(1)
        ok, _ = run("adb start-server")
        time.sleep(1)
        status = get_status()
        print(f"✓ Restarted. Status: {status}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
