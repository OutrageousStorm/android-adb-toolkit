#!/usr/bin/env python3
"""
adb-settings.py -- Read/write all Android system settings via ADB
Usage: python3 adb-settings.py get global limit_ad_tracking
       python3 adb-settings.py set secure location_mode 0
       python3 adb-settings.py dump global > settings_backup.json
"""
import subprocess, json, sys, argparse

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_setting(namespace, key):
    val = adb(f"settings get {namespace} {key}")
    return val if val != "null" else None

def set_setting(namespace, key, val):
    adb(f"settings put {namespace} {key} {val}")

def dump_namespace(namespace):
    out = adb(f"settings list {namespace}")
    settings = {}
    for line in out.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            settings[k.strip()] = v.strip()
    return settings

def main():
    parser = argparse.ArgumentParser(description="Manage Android system settings")
    parser.add_argument("action", choices=["get", "set", "dump"])
    parser.add_argument("namespace", choices=["global", "secure", "system"])
    parser.add_argument("key", nargs="?")
    parser.add_argument("value", nargs="?")
    args = parser.parse_args()

    if args.action == "get":
        if not args.key:
            print("Usage: adb-settings.py get <namespace> <key>")
            sys.exit(1)
        val = get_setting(args.namespace, args.key)
        print(f"{args.key} = {val or '(not set)'}")

    elif args.action == "set":
        if not args.key or args.value is None:
            print("Usage: adb-settings.py set <namespace> <key> <value>")
            sys.exit(1)
        set_setting(args.namespace, args.key, args.value)
        print(f"✓ {args.namespace}/{args.key} = {args.value}")

    elif args.action == "dump":
        settings = dump_namespace(args.namespace)
        json.dump(settings, sys.stdout, indent=2)

if __name__ == "__main__":
    main()
