#!/usr/bin/env python3
"""
device_screencap.py -- Continuous screenshot capture from Android device
Usage: python3 device_screencap.py --interval 2 --output ./screenshots
       Captures one every 2 seconds to a folder
"""
import subprocess, os, sys, argparse, time
from pathlib import Path
from datetime import datetime

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def screencap(output_dir, filename=None):
    if not filename:
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    out_path = Path(output_dir) / filename
    result = subprocess.run(
        f"adb exec-out screencap -p > {out_path}",
        shell=True, capture_output=True, text=True
    )
    return out_path if out_path.stat().st_size > 0 else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between captures")
    parser.add_argument("--output", default="./screenshots", help="Output directory")
    parser.add_argument("--count", type=int, help="Stop after N captures")
    parser.add_argument("--burst", type=int, help="Rapid burst of N screenshots")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📸 Device Screenshot Capture")
    print(f"Output: {out_dir.resolve()}")
    
    if args.burst:
        print(f"Burst mode: {args.burst} rapid captures\n")
        for i in range(args.burst):
            path = screencap(out_dir)
            if path:
                print(f"  [{i+1}/{args.burst}] {path.name}")
            time.sleep(0.1)
        print(f"\n✅ Burst complete: {args.burst} screenshots")
        return

    count = 0
    try:
        while True:
            path = screencap(out_dir)
            if path:
                count += 1
                ts = datetime.now().strftime("%H:%M:%S")
                print(f"[{ts}] {path.name}")
            if args.count and count >= args.count:
                print(f"\nStopped after {count} captures.")
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\n✅ Captured {count} screenshots.")

if __name__ == "__main__":
    main()
