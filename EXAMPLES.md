# ADB Toolkit Examples

Real-world usage examples for common tasks.

## 1. Backup all installed apps

```bash
# Extract all user APKs
python3 tools/app_extractor.py --output ./backups/

# Or manually
for pkg in $(adb shell pm list packages -3 | cut -d: -f2); do
  path=$(adb shell pm path $pkg | cut -d: -f2)
  adb pull $path backups/${pkg}.apk
done
```

## 2. Mass-install APKs

```bash
for apk in *.apk; do
  adb install -r "$apk"
done
```

## 3. Monitor network in real-time

```bash
# See all connections from device
python3 tools/network_monitor.py --interval 1

# Or watch specific app
python3 tools/network_monitor.py --filter com.whatsapp
```

## 4. Audit permissions

```bash
# Scan all installed apps for dangerous perms
python3 tools/permission_audit.py --user-only

# Save to CSV for review
python3 tools/permission_audit.py --csv audit.csv

# Revoke location from Facebook
adb shell pm revoke com.facebook.katana android.permission.ACCESS_FINE_LOCATION
```

## 5. Device info snapshot

```bash
python3 tools/device_info.py

# Output: full specs, CPU freq, storage, battery, network, security status
```

## 6. Find and clear large cache

```bash
# Find files > 100MB
adb shell find /data/data -size +100M 2>/dev/null

# Or use the tool
python3 tools/find-large-files.py --min-size 100M

# Clear app cache
adb shell pm trim-caches 10G
```

## 7. Monitor battery drain in real-time

```bash
# Watch battery % and temp every 5 seconds
while true; do
  adb shell dumpsys battery | grep -E "level|temp"
  sleep 5
done
```

## 8. Disable bloatware safely

```bash
python3 tools/smart_debloat.sh lists/samsung.txt

# Or uninstall to user only (reversible)
adb shell pm uninstall -k --user 0 com.facebook.katana
```
