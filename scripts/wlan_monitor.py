#!/usr/bin/env python3
"""
wlan_monitor.py -- Monitor WiFi signal strength and frequency in real-time
Shows RSSI, link speed, frequency, and suggests optimal placement.
Usage: python3 wlan_monitor.py [--interval 2] [--threshold -70]
"""
import subprocess, time, re, argparse, os
from datetime import datetime

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_wifi_info():
    out = adb("dumpsys wifi | grep -E '(mRssi|mLinkSpeed|mFrequency|SSID)'")
    info = {}
    for line in out.splitlines():
        if 'mRssi' in line:
            m = re.search(r'mRssi=(-?\d+)', line)
            if m: info['rssi'] = int(m.group(1))
        if 'mLinkSpeed' in line:
            m = re.search(r'mLinkSpeed=(\d+)', line)
            if m: info['speed'] = int(m.group(1))
        if 'mFrequency' in line:
            m = re.search(r'mFrequency=(\d+)', line)
            if m: info['freq'] = int(m.group(1))
    
    ssid = adb("settings get global wifi_network_name") or "unknown"
    info['ssid'] = ssid
    return info

def rssi_quality(rssi):
    """Convert RSSI to percentage"""
    if rssi >= -50: return 100
    if rssi <= -100: return 0
    return 2 * (rssi + 100)

def rssi_rating(rssi):
    """Human-readable WiFi quality"""
    q = rssi_quality(rssi)
    if q >= 80: return "Excellent"
    if q >= 60: return "Good"
    if q >= 40: return "Fair"
    if q >= 20: return "Weak"
    return "Very Weak"

def freq_band(freq):
    """2.4GHz vs 5GHz"""
    if 2400 <= freq <= 2500: return "2.4GHz"
    if 5000 <= freq <= 6000: return "5GHz"
    return "Unknown"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--threshold", type=int, default=-70, help="Alert if below this dBm")
    args = parser.parse_args()

    print("\n📶 WiFi Monitor (Ctrl+C to stop)\n")
    try:
        while True:
            os.system('clear' if os.name != 'nt' else 'cls')
            info = get_wifi_info()
            
            rssi = info.get('rssi', -100)
            speed = info.get('speed', 0)
            freq = info.get('freq', 0)
            ssid = info.get('ssid', '?')
            
            q = rssi_quality(rssi)
            rating = rssi_rating(rssi)
            band = freq_band(freq)
            
            # Signal bar
            bars = int(q / 10)
            bar = "█" * bars + "░" * (10 - bars)
            
            print(f"📶 WiFi Monitor — {datetime.now().strftime('%H:%M:%S')}")
            print(f"\n  SSID:    {ssid}")
            print(f"  Signal:  {bar} {q}% ({rssi} dBm) — {rating}")
            print(f"  Speed:   {speed} Mbps")
            print(f"  Band:    {band} ({freq} MHz)")
            
            if rssi < args.threshold:
                print(f"\n  ⚠️  WARNING: Signal below {args.threshold} dBm")
                print(f"  📍 Move closer to router or adjust antenna orientation")
            
            print(f"\nRefreshing every {args.interval}s...")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
