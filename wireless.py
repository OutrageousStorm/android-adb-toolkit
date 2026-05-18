#!/usr/bin/env python3
"""
wireless.py -- Manage wireless ADB connections
Connect/disconnect Android devices over WiFi without USB.
Usage: python3 wireless.py [--connect IP] [--pair IP PIN] [--list]
"""
import subprocess, sys, argparse, re, time

def adb(cmd):
    r = subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip(), r.returncode

def get_devices():
    out, _ = adb("devices")
    devices = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices

def pair_device(ip, port=5555):
    """Get pairing code on device: Settings → Developer Options → Wireless debugging → Show pairing code"""
    print(f"\n🔐 Pairing with {ip}:{port}")
    print("Go to: Settings → Developer Options → Wireless debugging → Show pairing code")
    code = input("Enter 6-digit pairing code: ").strip()
    
    out, rc = adb(f"pair {ip}:{port}")
    if rc != 0:
        print(f"Pairing failed: {out}")
        return False
    
    print(f"✅ Paired with {ip}")
    return True

def connect_device(ip, port=5555):
    """Connect to already-paired device"""
    print(f"Connecting to {ip}:{port}...")
    out, rc = adb(f"connect {ip}:{port}")
    if rc == 0 and "connected" in out.lower():
        print(f"✅ Connected to {ip}")
        return True
    else:
        print(f"❌ Connection failed: {out}")
        return False

def disconnect_device(ip):
    """Disconnect wireless device"""
    out, _ = adb(f"disconnect {ip}")
    print(f"✅ Disconnected {ip}")

def list_devices():
    """Show all connected devices"""
    devices = get_devices()
    if not devices:
        print("No devices connected.")
        return
    
    print(f"\n📱 Connected devices ({len(devices)}):")
    for dev in devices:
        is_wireless = ":" in dev
        icon = "📡" if is_wireless else "🔌"
        print(f"  {icon}  {dev}")

def main():
    parser = argparse.ArgumentParser(description="Wireless ADB manager")
    parser.add_argument("--pair", metavar="IP", help="Pair with device (requires pairing code)")
    parser.add_argument("--connect", metavar="IP", help="Connect to paired device")
    parser.add_argument("--disconnect", metavar="IP", help="Disconnect device")
    parser.add_argument("--list", action="store_true", help="List all devices")
    parser.add_argument("--port", type=int, default=5555)
    args = parser.parse_args()

    if args.pair:
        pair_device(args.pair, args.port)
    elif args.connect:
        connect_device(args.connect, args.port)
    elif args.disconnect:
        disconnect_device(args.disconnect)
    elif args.list or not any([args.pair, args.connect, args.disconnect]):
        list_devices()

if __name__ == "__main__":
    main()
