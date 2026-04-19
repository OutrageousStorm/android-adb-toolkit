#!/usr/bin/env node
/**
 * adb-cli.js -- Command-line ADB wrapper with common shortcuts
 * Usage: node adb-cli.js [command] [args]
 * Examples:
 *   node adb-cli.js info              (device info)
 *   node adb-cli.js clean <package>   (clear app data)
 *   node adb-cli.js pull-apks         (extract all user APKs)
 *   node adb-cli.js top-apps          (top battery consumers)
 */

const { execSync } = require('child_process');

const COMMANDS = {
  info: "adb shell \"echo 'Device:' && getprop ro.product.model && echo 'Android:' && getprop ro.build.version.release && echo 'Serial:' && getprop ro.serialno\"",
  
  clean: (pkg) => `adb shell pm clear ${pkg} && echo "✓ Cleared ${pkg}"`,
  
  'pull-apks': `adb shell pm list packages -3 | awk -F: '{print $2}' | while read pkg; do 
    path=$(adb shell pm path "$pkg" | cut -d: -f2); 
    [ -n "$path" ] && adb pull "$path" "${pkg}.apk" 2>/dev/null && echo "✓ $pkg"
  done`,
  
  'top-apps': "adb shell dumpsys batterystats | grep 'uid' | head -10",
  
  'screen-record': (duration = 30) => `adb shell screenrecord --time-limit ${duration} /sdcard/record.mp4 && adb pull /sdcard/record.mp4 . && echo "✓ Saved to record.mp4"`,
  
  screenshot: "adb exec-out screencap -p > screenshot_$(date +%s).png && echo '✓ Screenshot saved'",
  
  reboot: "adb reboot && echo 'Rebooting...'",
  'reboot-recovery': "adb reboot recovery && echo 'Rebooting to recovery...'",
  'reboot-bootloader': "adb reboot bootloader && echo 'Rebooting to bootloader...'",
};

function run(cmd) {
  try {
    const result = execSync(cmd, { encoding: 'utf-8', stdio: 'inherit' });
    return result;
  } catch(e) {
    console.error(`✗ Error: ${e.message}`);
    process.exit(1);
  }
}

function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  
  if (!cmd || cmd === '--help' || cmd === '-h') {
    console.log('adb-cli — ADB command shortcuts\n');
    console.log('Commands:');
    Object.keys(COMMANDS).forEach(c => {
      console.log(`  ${c}`);
    });
    return;
  }
  
  const handler = COMMANDS[cmd];
  if (!handler) {
    console.error(`Unknown command: ${cmd}`);
    process.exit(1);
  }
  
  const actualCmd = typeof handler === 'function' 
    ? handler(...args.slice(1))
    : handler;
  
  run(actualCmd);
}

main();
