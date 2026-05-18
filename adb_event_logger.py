#!/usr/bin/env python3
"""
adb_event_logger.py -- Log all ADB events (screen, network, sensor, calls, SMS)
Real-time Android event stream to JSON.
Usage: python3 adb_event_logger.py --output events.jsonl [--filter events=call,sms]
"""
import subprocess, json, re, sys, argparse, time
from datetime import datetime

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def stream_logcat(output_file, filters=None):
    print("📡 ADB Event Logger — press Ctrl+C to stop\\n")
    
    proc = subprocess.Popen(
        "adb logcat -v threadtime *:D",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )

    patterns = {
        "screen": (r"PowerManagerService.*?state=(\d+)", "screen"),
        "call": (r"CallManager.*?Phone State: (\w+)", "phone_call"),
        "sms": (r"SMSDispatcher.*?message from (\+?[\d\s\-]+)", "sms_received"),
        "network": (r"ConnectivityManager.*?state=(\w+)", "network"),
        "battery": (r"BatteryManager.*?level=(\d+)", "battery"),
        "location": (r"LocationManager.*?(FINE|COARSE).*?enabled", "location"),
    }

    if output_file:
        f = open(output_file, 'a')
    else:
        f = sys.stdout

    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break

            for event_type, (pattern, label) in patterns.items():
                if filters and event_type not in filters:
                    continue
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    event = {
                        "timestamp": datetime.now().isoformat(),
                        "type": label,
                        "value": m.group(1),
                        "raw": line[:200]
                    }
                    f.write(json.dumps(event) + "\\n")
                    f.flush()
                    print(f"[{label}] {m.group(1)}")
    except KeyboardInterrupt:
        print("\\nStopped.")
    finally:
        proc.terminate()
        if output_file:
            f.close()
            print(f"\\nLogged to {output_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="JSONL output file (omit for stdout)")
    parser.add_argument("--filter", help="Comma-separated event types: screen,call,sms,network,battery,location")
    args = parser.parse_args()

    filters = args.filter.split(',') if args.filter else None
    stream_logcat(args.output, filters)

if __name__ == "__main__":
    main()
