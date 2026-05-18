#!/usr/bin/env python3
"""
battery_report.py -- Generate detailed battery health report
Usage: python3 battery_report.py [--json output.json]
"""
import subprocess, json, re
from datetime import datetime

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def parse_battery():
    out = adb("dumpsys battery")
    battery = {}
    for line in out.splitlines():
        m = re.match(r'\s*(\w+):\s*(.+)', line)
        if m:
            k, v = m.group(1), m.group(2)
            battery[k.lower()] = v
    return battery

def parse_health_history():
    out = adb("dumpsys battery --history | head -50")
    return out

def main():
    print("\n🔋 Battery Report Generator")
    print("=" * 50)
    
    battery = parse_battery()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "current_status": {
            "level": battery.get("level", "?"),
            "temperature": battery.get("temperature", "?"),
            "voltage": battery.get("voltage", "?"),
            "health": battery.get("health", "?"),
            "status": battery.get("status", "?"),
        },
        "charging": {
            "plugged": battery.get("plugged", "?"),
            "present": battery.get("present", "?"),
        }
    }
    
    print(f"\n  Level:       {report['current_status']['level']}%")
    print(f"  Health:      {report['current_status']['health']}")
    print(f"  Temperature: {report['current_status']['temperature']}°C")
    print(f"  Voltage:     {report['current_status']['voltage']}mV")
    print(f"  Status:      {report['current_status']['status']}")
    print(f"  Plugged:     {report['charging']['plugged']}")
    
    print("\n✅ Report generated")
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", help="Export to JSON")
    args = parser.parse_args()
    
    if args.json:
        with open(args.json, "w") as f:
            json.dump(report, f, indent=2)
        print(f"  Saved to {args.json}")

if __name__ == "__main__":
    main()
