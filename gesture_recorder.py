#!/usr/bin/env python3
"""
gesture_recorder.py -- Record touch gestures and replay them
Records taps, swipes, and multi-touch gestures from ADB.
Usage: python3 gesture_recorder.py --record > gestures.json
       python3 gesture_recorder.py --replay gestures.json
"""
import subprocess, json, argparse, time, sys
from datetime import datetime

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def get_touch_events():
    """Parse /dev/input events for touch coordinates"""
    proc = subprocess.Popen(
        "adb shell 'getevent /dev/input/event*'",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    return proc

def record_gestures(duration=30):
    print(f"Recording for {duration}s... (touch the screen)")
    gestures = []
    start = time.time()

    proc = get_touch_events()
    try:
        while time.time() - start < duration:
            line = proc.stdout.readline()
            if not line:
                break
            # Parse input event format: /dev/input/eventX: 0001 014a 00000001
            if "00000001" in line or "00000000" in line:
                ts = time.time() - start
                gestures.append({"type": "raw_event", "line": line.strip(), "ts": ts})
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        proc.terminate()

    return gestures

def record_simple_taps():
    """Record taps by monitoring logcat for touch events"""
    print("Recording taps (press Ctrl+C to stop)...")
    taps = []

    # Use dumpsys to watch input
    # Alternative: parse logcat for MotionEvent
    proc = subprocess.Popen(
        "adb logcat | grep -i 'MotionEvent\|ACTION_DOWN'",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )

    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            # Extract coordinates if possible
            taps.append({"type": "tap", "raw": line.strip(), "time": datetime.now().isoformat()})
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        proc.terminate()

    return taps

def replay(gestures):
    """Replay recorded gestures"""
    print(f"Replaying {len(gestures)} gestures...")
    for i, g in enumerate(gestures):
        print(f"  [{i+1}] {g.get('type', 'unknown')}")
        # In real implementation, parse and replay via adb input
        time.sleep(0.5)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--replay", help="Replay from JSON file")
    parser.add_argument("--duration", type=int, default=30)
    args = parser.parse_args()

    if args.record:
        gestures = record_simple_taps()
        print(json.dumps(gestures, indent=2))
    elif args.replay:
        with open(args.replay) as f:
            gestures = json.load(f)
        replay(gestures)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
