#!/usr/bin/env python3
"""
cli.py -- Command-line interface for android-adb-toolkit
Faster than web UI for power users.
Usage: python3 cli.py <command> [args]
"""
import subprocess, sys, argparse, json
from datetime import datetime

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def list_apps(user_only=False):
    flag = "-3" if user_only else ""
    out = adb(f"pm list packages {flag}")
    return [l.split(":")[1] for l in out.splitlines() if l.startswith("package:")]

def get_device_info():
    return {
        "model": adb("getprop ro.product.model"),
        "android": adb("getprop ro.build.version.release"),
        "api": adb("getprop ro.build.version.sdk"),
        "device": adb("getprop ro.product.device"),
        "serial": adb("getprop ro.serialno"),
    }

def main():
    parser = argparse.ArgumentParser(prog="adb-cli")
    subparsers = parser.add_subparsers(dest="cmd")

    # Device info
    subparsers.add_parser("info", help="Show device info")

    # Apps
    app_p = subparsers.add_parser("apps", help="List installed apps")
    app_p.add_argument("--user-only", action="store_true")
    app_p.add_argument("--json", action="store_true")

    # Debloat
    debloat_p = subparsers.add_parser("debloat", help="Remove app")
    debloat_p.add_argument("pkg", help="Package name")

    # Install
    inst_p = subparsers.add_parser("install", help="Install APK")
    inst_p.add_argument("apk", help="Path to APK")

    # Screenshot
    subparsers.add_parser("screenshot", help="Take screenshot")

    # Battery
    subparsers.add_parser("battery", help="Show battery info")

    args = parser.parse_args()

    if args.cmd == "info":
        info = get_device_info()
        for k, v in info.items():
            print(f"  {k:<12} {v}")

    elif args.cmd == "apps":
        apps = list_apps(args.user_only)
        if args.json:
            print(json.dumps(apps))
        else:
            for i, app in enumerate(apps, 1):
                print(f"  {i:3d}. {app}")

    elif args.cmd == "debloat":
        result = adb(f"pm uninstall -k --user 0 {args.pkg}")
        print(f"  {'✓' if 'Success' in result else '✗'} {args.pkg}")

    elif args.cmd == "install":
        result = adb(f"install -r {args.apk}")
        print(f"  {result}")

    elif args.cmd == "screenshot":
        subprocess.run(f"adb exec-out screencap -p > screenshot_{datetime.now().strftime('%H%M%S')}.png", shell=True)
        print("  ✓ Screenshot saved")

    elif args.cmd == "battery":
        info = adb("dumpsys battery")
        for line in info.splitlines()[:10]:
            print(f"  {line}")

if __name__ == "__main__":
    main()
