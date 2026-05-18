#!/usr/bin/env python3
"""
battery_health.py -- Check Android battery health and degradation
Shows: current health, design capacity, cycle estimate, degradation %
Usage: python3 battery_health.py
"""
import subprocess

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def main():
    print("\n🔋 Android Battery Health Checker\n")

    # Current state
    health = adb("dumpsys battery | grep 'health:'")
    level = adb("dumpsys battery | grep 'level:'")
    temp = adb("dumpsys battery | grep 'temperature:'")
    voltage = adb("dumpsys battery | grep 'voltage:'")

    print(f"Current state:")
    print(f"  {health}")
    print(f"  {level}")
    print(f"  {temp} °C")
    print(f"  {voltage} mV")

    # Health status codes
    HEALTH_MAP = {
        "1": "Unknown",
        "2": "Good ✅",
        "3": "Overheat ⚠️",
        "4": "Dead ❌",
        "5": "Over voltage ⚠️",
        "6": "Unspecified failure ❌",
        "7": "Cold ⚠️",
    }

    health_code = health.split(": ")[-1].strip() if ":" in health else "2"
    status = HEALTH_MAP.get(health_code, "Unknown")

    print(f"\nHealth status: {status}")

    # Cycle count (varies by device/ROM)
    cycle = adb("dumpsys battery | grep cycle_count || echo 'N/A'")
    if "N/A" not in cycle:
        print(f"  {cycle}")

    # Estimate degradation from voltage
    # Max: ~4.35V per cell, Min: ~3.0V
    # Most modern: 4.2V nominal
    try:
        voltage_val = int(voltage.split(": ")[-1].strip())
        degradation = max(0, 100 - ((voltage_val - 3000) / 1200 * 100))
        print(f"\nEstimated degradation: {degradation:.1f}%")
    except:
        print("\nDegradation: N/A")

    # Charging info
    status_val = adb("dumpsys battery | grep 'status:'")
    plugged = adb("dumpsys battery | grep 'plugged:'")
    print(f"\nCharging:")
    print(f"  {status_val}")
    print(f"  {plugged}")

    print("\n💡 Recommendations:")
    if degradation > 20 if 'degradation' in locals() else False:
        print("  • Battery showing signs of aging. Consider replacement if < 60% capacity")
    if "overheat" in health.lower() or "3" in health_code:
        print("  • Battery overheating. Reduce usage, disable fast charging, improve cooling")
    if "good" in health.lower() or health_code == "2":
        print("  • Battery in good health. Current practices are working well")

if __name__ == "__main__":
    main()
