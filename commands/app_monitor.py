#!/usr/bin/env python3
"""
app_monitor.py -- Monitor app launches, crashes, and ANRs in real-time
Usage: python3 app_monitor.py [--filter keyword]
"""
import subprocess, re, sys
from datetime import datetime

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout

def stream_logcat(filter_kw=None):
    proc = subprocess.Popen(
        "adb logcat -v time *:I",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    print("\n📱 App Monitor — Ctrl+C to stop\n")
    print(f"{'Time':<12} {'Event':<10} {'Package':<35} {'Details'}")
    print("─" * 80)
    
    try:
        while True:
            line = proc.stdout.readline()
            if not line: break
            
            # App launch
            if "START" in line and "Intent" in line:
                pkg_m = re.search(r'cmp=([^\s/]+)', line)
                if pkg_m:
                    pkg = pkg_m.group(1)
                    if filter_kw and filter_kw.lower() not in pkg.lower(): continue
                    ts = datetime.now().strftime("%H:%M:%S")
                    print(f"{ts:<12} {'LAUNCH':<10} {pkg:<35} OK")
            
            # Crash
            if "FATAL EXCEPTION" in line or "AndroidRuntime: FATAL" in line:
                pkg_m = re.search(r'Process: ([\w.]+)', line)
                if pkg_m:
                    pkg = pkg_m.group(1)
                    if filter_kw and filter_kw.lower() not in pkg.lower(): continue
                    ts = datetime.now().strftime("%H:%M:%S")
                    exc_m = re.search(r'(\w+Exception):', line)
                    exc = exc_m.group(1) if exc_m else "CRASH"
                    print(f"{ts:<12} {'CRASH':<10} {pkg:<35} {exc}")
            
            # ANR
            if "Application Not Responding" in line:
                pkg_m = re.search(r'([\w.]+) \(pid', line)
                if pkg_m:
                    pkg = pkg_m.group(1)
                    if filter_kw and filter_kw.lower() not in pkg.lower(): continue
                    ts = datetime.now().strftime("%H:%M:%S")
                    print(f"{ts:<12} {'ANR':<10} {pkg:<35} Blocked")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        proc.terminate()

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--filter", help="Filter by package keyword")
    args = p.parse_args()
    stream_logcat(args.filter)
