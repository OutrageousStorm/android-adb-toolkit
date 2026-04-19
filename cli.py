#!/usr/bin/env python3
"""
cli.py -- Command-line interface for ADB operations
Powers the web UI but also works standalone.
Usage: python3 cli.py device-info
       python3 cli.py install-apk path/to/app.apk
       python3 cli.py debloat --confirm
"""
import subprocess, sys, argparse, json
from pathlib import Path

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def device_info():
    info = {
        "model": adb("getprop ro.product.model"),
        "android": adb("getprop ro.build.version.release"),
        "api": adb("getprop ro.build.version.sdk"),
        "serial": adb("getprop ro.serialno"),
        "fingerprint": adb("getprop ro.build.fingerprint"),
    }
    return info

def install_apk(path):
    if not Path(path).exists():
        return {"error": f"APK not found: {path}"}
    result = subprocess.run(f"adb install {path}", shell=True, capture_output=True, text=True)
    return {"success": "Success" in result.stdout}

def list_packages(user_only=False):
    flag = "-3" if user_only else ""
    out = adb(f"pm list packages {flag}")
    return [l.split(":")[1] for l in out.splitlines() if l.startswith("package:")]

def debloat_safe(confirm=False):
    SAFE_REMOVABLE = [
        "com.facebook.katana", "com.facebook.appmanager", "com.facebook.services",
        "com.instagram.android", "com.twitter.android", "com.snapchat.android",
        "com.netflix.mediaclient", "com.spotify.music",
    ]
    installed = set(list_packages(user_only=True))
    targets = [p for p in SAFE_REMOVABLE if p in installed]
    
    if not confirm:
        return {"count": len(targets), "packages": targets, "confirm_needed": True}
    
    removed = []
    for pkg in targets:
        r = adb(f"pm uninstall -k --user 0 {pkg}")
        if "Success" in r:
            removed.append(pkg)
    return {"removed": removed, "count": len(removed)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["device-info", "install-apk", "list-apps", "debloat"])
    parser.add_argument("--apk", help="APK file for install-apk")
    parser.add_argument("--user-only", action="store_true", help="List user apps only")
    parser.add_argument("--confirm", action="store_true", help="Confirm debloat")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.command == "device-info":
        result = device_info()
    elif args.command == "install-apk":
        if not args.apk:
            print("--apk required"); sys.exit(1)
        result = install_apk(args.apk)
    elif args.command == "list-apps":
        result = {"packages": list_packages(args.user_only)}
    elif args.command == "debloat":
        result = debloat_safe(args.confirm)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            if isinstance(v, list) and len(v) > 3:
                print(f"{k}: {len(v)} items")
            else:
                print(f"{k}: {v}")

if __name__ == "__main__":
    main()
