#!/usr/bin/env python3
"""device_clone.py - Clone all settings from one device to another"""
import subprocess, sys

def adb(cmd, device=None):
    prefix = f"-s {device}" if device else ""
    r = subprocess.run(f"adb {prefix} shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def clone_settings(source, target):
    print(f"\n📋 Cloning {source} → {target}\n")
    
    for namespace in ['global', 'secure', 'system']:
        print(f"  Cloning {namespace} settings...")
        out = adb(f"settings list {namespace}", source)
        count = 0
        for line in out.splitlines():
            if '=' not in line:
                continue
            key, val = line.split('=', 1)
            adb(f"settings put {namespace} {key} {val}", target)
            count += 1
        print(f"    ✓ {count} settings cloned")
    
    print(f"\n✅ Clone complete!")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: device_clone.py <source_device> <target_device>")
        sys.exit(1)
    clone_settings(sys.argv[1], sys.argv[2])
