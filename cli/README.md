# ADB Toolkit CLI

Node.js CLI companion for the [ADB Toolkit web app](https://github.com/OutrageousStorm/android-adb-toolkit).

## Install
```bash
cd cli/
npm install
npm link   # makes `adb-toolkit` available globally
```

## Commands
```bash
adb-toolkit info                              # device summary
adb-toolkit screenshot                        # save screenshot to disk
adb-toolkit screenshot -o screen.png          # custom filename
adb-toolkit perms --pkg com.facebook.katana   # list dangerous perms
adb-toolkit perms --pkg com.facebook.katana --revoke  # revoke them
adb-toolkit packages --user                   # list user-installed apps
adb-toolkit packages --filter google          # search packages
adb-toolkit type "hello world"                # type text on device
```
