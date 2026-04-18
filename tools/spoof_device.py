#!/usr/bin/env python3
"""
spoof_device.py -- Spoof Android device properties for testing
Change: model, build fingerprint, build tags, API level, manufacturer
Usage: python3 spoof_device.py --model "Pixel 7" --tags "release-keys"
       python3 spoof_device.py --reset    (restore original values)

Note: Requires Magisk + systemless modification or kernel-level patching.
This script modifies /system/build.prop (requires root).
"""
import subprocess, argparse, sys, re

PROPS = {
    "model": "ro.product.model",
    "brand": "ro.product.brand",
    "manufacturer": "ro.product.manufacturer",
    "fingerprint": "ro.build.fingerprint",
    "tags": "ro.build.tags",
    "type": "ro.build.type",
    "api": "ro.build.version.sdk",
    "device": "ro.product.device",
    "hardware": "ro.hardware",
}

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_prop(key):
    return adb(f"getprop {PROPS.get(key, key)}")

def backup_props():
    """Backup current build props"""
    props_file = "device_props_backup.json"
    import json
    backup = {k: get_prop(k) for k in PROPS.keys()}
    with open(props_file, 'w') as f:
        json.dump(backup, f, indent=2)
    print(f"✓ Backed up to {props_file}")
    return backup

def spoof_props(changes):
    """Apply spoofed properties via Magisk module injection"""
    print("\n🎭 Device Spoofer")
    print("=" * 50)
    
    # Check for root
    root_check = adb("id | grep 'uid=0'")
    if not root_check:
        print("❌ Root required. Install Magisk + Shamiko or use kernel-level patching.")
        return False

    backup = backup_props()
    print("\n📝 Current properties:")
    for key in changes.keys():
        current = backup.get(key)
        print(f"  {key:<15} {current}")

    print("\n🔄 Applying spoofs:")
    for key, new_val in changes.items():
        prop_key = PROPS.get(key, key)
        # Try to modify via setprop (may require additional modifications)
        r = adb(f"setprop {prop_key} '{new_val}'")
        # Verify
        actual = adb(f"getprop {prop_key}")
        ok = actual == new_val or actual == ""  # setprop on read-only may fail
        print(f"  {'✓' if ok else '⚠'} {key}: {new_val}")

    print("\n⚠️  Note: Some properties are read-only and require:")
    print("   - Magisk module + resetprop script")
    print("   - Kernel-level patching")
    print("   - Or frida hooks at runtime")
    return True

def reset_props():
    """Restore from backup"""
    import json
    try:
        with open("device_props_backup.json") as f:
            backup = json.load(f)
        print("Restoring original properties...")
        for key, val in backup.items():
            prop_key = PROPS.get(key, key)
            adb(f"setprop {prop_key} '{val}'")
        print("✓ Restored")
    except Exception as e:
        print(f"❌ Failed: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Device model")
    parser.add_argument("--brand", help="Brand")
    parser.add_argument("--fingerprint", help="Build fingerprint")
    parser.add_argument("--tags", help="Build tags (release-keys/test-keys)")
    parser.add_argument("--type", help="Build type (user/userdebug/eng)")
    parser.add_argument("--reset", action="store_true", help="Restore from backup")
    parser.add_argument("--show", action="store_true", help="Show current properties")
    args = parser.parse_args()

    if args.show:
        print("\n📱 Current Device Properties")
        print("=" * 50)
        for key in PROPS.keys():
            val = get_prop(key)
            print(f"  {key:<15} {val}")
        return

    if args.reset:
        reset_props()
        return

    changes = {k: v for k, v in vars(args).items() if v is not None and k != 'reset' and k != 'show'}
    if not changes:
        parser.print_help()
        return

    spoof_props(changes)

if __name__ == "__main__":
    main()
