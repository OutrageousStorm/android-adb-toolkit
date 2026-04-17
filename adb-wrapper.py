#!/usr/bin/env python3
"""
adb-wrapper.py — Python CLI wrapper for common ADB tasks
Usage: python3 adb-wrapper.py install app.apk
       python3 adb-wrapper.py screenshot
       python3 adb-wrapper.py logcat
"""
import subprocess, sys, argparse, time
from pathlib import Path

def adb(cmd):
    r = subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()

def check_device():
    code, out = adb("devices")
    if "device" not in out or "offline" in out:
        print("❌ No device connected"); sys.exit(1)

def cmd_install(apk):
    if not Path(apk).exists():
        print(f"❌ {apk} not found"); return
    print(f"Installing {Path(apk).name}...")
    code, out = adb(f"install -r '{apk}'")
    print(f"{'✅' if code == 0 else '❌'} {out[:100]}")

def cmd_screenshot(out="screenshot.png"):
    adb(f"exec-out screencap -p > {out}")
    print(f"✅ Saved: {out}" if Path(out).exists() else "❌ Failed")

def cmd_logcat(filt=None):
    cmd = "logcat -v time" + (f" {filt}:D" if filt else "")
    try:
        subprocess.run(f"adb {cmd}", shell=True)
    except KeyboardInterrupt:
        print("\nStopped.")

def main():
    check_device()
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("install").add_argument("apk")
    sub.add_parser("screenshot").add_argument("output", nargs="?", default="screenshot.png")
    sub.add_parser("logcat").add_argument("filter", nargs="?")
    
    args = p.parse_args()
    if not args.cmd: p.print_help(); return
    
    if args.cmd == "install": cmd_install(args.apk)
    elif args.cmd == "screenshot": cmd_screenshot(args.output)
    elif args.cmd == "logcat": cmd_logcat(args.filter)

if __name__ == "__main__": main()
