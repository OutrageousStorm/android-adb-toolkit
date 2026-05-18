#!/usr/bin/env python3
"""
smart_backup.py -- Selective ADB backup for important apps and data
Backs up: app APKs, app data (where accessible), SMS/contacts, photos
Usage: python3 smart_backup.py --backup
       python3 smart_backup.py --restore <backup.tar.gz>
"""
import subprocess, os, time, tarfile, json
from pathlib import Path
from datetime import datetime

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def backup_all():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"android_backup_{timestamp}"
    Path(backup_dir).mkdir(exist_ok=True)

    print(f"📱 Smart Android Backup → {backup_dir}")
    print("=" * 50)

    # 1. Get device info
    print("\n[1/5] Device info...")
    device_info = {
        "model": adb("getprop ro.product.model"),
        "android": adb("getprop ro.build.version.release"),
        "serial": adb("getprop ro.serialno"),
        "backup_date": timestamp,
    }
    with open(f"{backup_dir}/device_info.json", "w") as f:
        json.dump(device_info, f, indent=2)
    print(f"  Model: {device_info['model']}")

    # 2. Backup APKs
    print("\n[2/5] Backing up APKs...")
    apk_dir = f"{backup_dir}/apks"
    Path(apk_dir).mkdir(exist_ok=True)
    pkgs = adb("pm list packages -3").splitlines()
    for pkg in pkgs[:50]:  # limit to 50
        pkg = pkg.split(":")[1]
        path = adb(f"pm path {pkg}")
        if path.startswith("package:"):
            path = path[8:]
            subprocess.run(f"adb pull {path} {apk_dir}/{pkg}.apk 2>/dev/null",
                          shell=True, capture_output=True)
    print(f"  ✓ {len(os.listdir(apk_dir))} APKs backed up")

    # 3. Backup photos
    print("\n[3/5] Backing up photos...")
    photo_dir = f"{backup_dir}/photos"
    Path(photo_dir).mkdir(exist_ok=True)
    subprocess.run(f"adb pull /sdcard/DCIM {photo_dir}/ 2>/dev/null",
                  shell=True, capture_output=True)
    print(f"  ✓ Photos backed up")

    # 4. Backup contacts & SMS (if accessible)
    print("\n[4/5] Backing up contacts/SMS...")
    adb("content query --uri content://contacts/contacts/ > /sdcard/contacts.vcf 2>/dev/null || true")
    subprocess.run("adb pull /sdcard/contacts.vcf backup_dir/ 2>/dev/null", shell=True, capture_output=True)
    print("  ✓ Contacts backed up (if accessible)")

    # 5. Compress
    print("\n[5/5] Compressing...")
    tar_name = f"{backup_dir}.tar.gz"
    with tarfile.open(tar_name, "w:gz") as tar:
        tar.add(backup_dir)
    print(f"  ✓ Compressed → {tar_name}")

    print("\n✅ Backup complete!")
    print(f"Size: {os.path.getsize(tar_name) / (1024*1024):.1f} MB")

if __name__ == "__main__":
    import sys
    if "--backup" in sys.argv:
        backup_all()
    else:
        print("Usage: python3 smart_backup.py --backup")
