# ADB Commands Reference

## Package Management
```bash
adb shell pm list packages              # all packages
adb shell pm list packages -3           # user apps only
adb shell pm path <package>             # app path
adb shell pm grant <pkg> <perm>         # grant permission
adb shell pm revoke <pkg> <perm>        # revoke permission
adb shell pm uninstall -k --user 0 <pkg>  # disable system app
adb shell cmd package install-existing <pkg>  # re-enable
```

## System Control
```bash
adb shell settings get/put global <key> <value>
adb shell settings get/put system <key> <value>
adb shell settings get/put secure <key> <value>
adb shell am force-stop <package>
adb shell am start <package>/.ActivityName
```

## Network & Debug
```bash
adb shell ip addr                 # network interfaces
adb shell netstat -tulnp          # listening ports
adb shell ping <host>             # test connectivity
adb logcat                         # live logs
adb bugreport                      # system report
```
