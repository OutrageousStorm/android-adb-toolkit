#!/usr/bin/env python3
"""
adb-profile-manager.py -- Save and restore ADB device profiles
Usage: python3 adb-profile-manager.py save <name>
       python3 adb-profile-manager.py load <name>
       python3 adb-profile-manager.py list
"""
import subprocess, json, sys, argparse
from pathlib import Path

PROFILES_FILE = Path.home() / '.adb_profiles.json'

def adb(cmd):
    r = subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_device():
    out = adb("devices")
    for line in out.splitlines()[1:]:
        if "device" in line and not line.startswith("*"):
            return line.split()[0]
    return None

def save_profile(name):
    device = get_device()
    if not device:
        print("No device connected")
        sys.exit(1)
    profiles = json.loads(PROFILES_FILE.read_text()) if PROFILES_FILE.exists() else {}
    profiles[name] = {
        'serial': device,
        'model': adb("shell getprop ro.product.model"),
        'android': adb("shell getprop ro.build.version.release"),
        'api': adb("shell getprop ro.build.version.sdk"),
    }
    PROFILES_FILE.write_text(json.dumps(profiles, indent=2))
    print(f"Saved: {name}")

def load_profile(name):
    profiles = json.loads(PROFILES_FILE.read_text()) if PROFILES_FILE.exists() else {}
    if name not in profiles:
        print(f"Profile not found: {name}")
        sys.exit(1)
    p = profiles[name]
    print(f"\nProfile: {name}")
    print(f"  Serial: {p['serial']}")
    print(f"  Model: {p['model']}")
    print(f"  Android: {p['android']} (API {p['api']})\n")

def list_profiles():
    if not PROFILES_FILE.exists():
        print("No profiles yet")
        return
    profiles = json.loads(PROFILES_FILE.read_text())
    if not profiles:
        print("No profiles")
        return
    print("\nSaved ADB profiles:\n")
    for name, p in profiles.items():
        print(f"  {name:<20} {p['serial']:<15} {p['model']} (Android {p['android']})")
    print()

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.add_parser('save', help='Save device').add_argument('name')
    subparsers.add_parser('load', help='Show profile').add_argument('name')
    subparsers.add_parser('list', help='List all')
    args = parser.parse_args()
    if args.cmd == 'save': save_profile(args.name)
    elif args.cmd == 'load': load_profile(args.name)
    elif args.cmd == 'list': list_profiles()
    else: parser.print_help()

if __name__ == "__main__":
    main()
