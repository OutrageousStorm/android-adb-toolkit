#!/usr/bin/env python3
"""pm-helper.py - Android PackageManager helper"""
import subprocess

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def list_apps(user_only=True):
    flag = "-3" if user_only else ""
    out = adb(f"pm list packages {flag}")
    return [l.split(":")[1] for l in out.splitlines() if l.startswith("package:")]

def get_size(pkg):
    out = adb(f"du -sh /data/data/{pkg}")
    return out.split()[0] if out else "?"

def main():
    print("📦 App Sizes:")
    for pkg in sorted(list_apps())[:10]:
        size = get_size(pkg)
        print(f"  {pkg.split('.')[-1]:<20} {size}")

if __name__ == "__main__":
    main()
