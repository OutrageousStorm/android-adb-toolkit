#!/usr/bin/env python3
"""
input_recorder.py -- Record tap/swipe sequences for automation
Usage: python3 input_recorder.py --tap 540 960 --tap 540 1200
"""
import subprocess, argparse, time

def adb(cmd):
    subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True)

def tap(x, y, delay=0):
    adb(f"input tap {x} {y}")
    if delay > 0:
        time.sleep(delay)

def swipe(x1, y1, x2, y2, duration=500):
    adb(f"input swipe {x1} {y1} {x2} {y2} {duration}")

def main():
    parser = argparse.ArgumentParser(description="Record user input for automation")
    parser.add_argument("--tap", nargs=2, type=int, metavar=("X", "Y"), help="Tap at coordinates")
    parser.add_argument("--swipe", nargs=4, type=int, metavar=("X1", "Y1", "X2", "Y2"), help="Swipe from X1,Y1 to X2,Y2")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between actions")
    args = parser.parse_args()

    if args.tap:
        print(f"Tapping {args.tap[0]}, {args.tap[1]}")
        tap(args.tap[0], args.tap[1], args.delay)
    elif args.swipe:
        print(f"Swiping ({args.swipe[0]},{args.swipe[1]}) to ({args.swipe[2]},{args.swipe[3]})")
        swipe(args.swipe[0], args.swipe[1], args.swipe[2], args.swipe[3])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
