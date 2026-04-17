# Advanced ADB Tricks

## 1. Connect multiple devices

```bash
adb devices                    # list all
adb -s <serial> shell <cmd>   # run on specific device
adb -s <serial> push file.txt /sdcard/
```

For over-the-air:
```bash
adb tcpip 5555                # enable on first device
adb connect 192.168.1.100:5555
```

## 2. Remote debugging (port forwarding)

```bash
adb forward tcp:8080 tcp:8080    # host:8080 → device:8080 (local)
adb forward tcp:8080 localabstract:webview_devtools  # Chrome DevTools
adb reverse tcp:8888 tcp:3000    # device:8888 → host:3000
```

## 3. Monkey testing (fuzzing)

```bash
# Random events on app
adb shell monkey -p com.example.app 10000

# Specific event distribution
adb shell monkey -p com.example.app -s 123   --pct-touch 50 --pct-motion 30 --pct-appswitch 10 5000
```

## 4. Battery statistics deep dive

```bash
adb shell dumpsys batterystats --reset  # reset history
# Use device for a few hours...
adb shell dumpsys batterystats | grep "Uid"  # per-app drain
adb bugreport bugreport.zip  # full report for Battery Historian
```

## 5. Network traffic analysis

```bash
adb shell tcpdump -i any -D              # list interfaces
adb shell tcpdump -i any -w /sdcard/capture.pcap -c 1000

# View on PC:
adb pull /sdcard/capture.pcap
wireshark capture.pcap
```

## 6. Kernel module inspection

```bash
adb shell lsmod                          # loaded modules
adb shell cat /proc/modules
adb shell cat /sys/module/<name>/parameters/
```

## 7. Debuggable app inspection

```bash
# For apps built with android:debuggable="true"
adb shell am start -D -S com.example.app  # start with debugger waiting
# Connect Android Studio or remote debugger to :8700
```

## 8. Custom ro.build properties (requires root)

```bash
adb shell getprop ro.build.fingerprint
adb shell setprop ro.build.fingerprint "google/sailfish/sailfish:11:RP1A.201005.004.A1:6838057:user/release-keys"
```
