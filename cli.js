#!/usr/bin/env node
/**
 * adb-toolkit CLI — Node.js wrapper for common ADB operations
 * Usage: npx android-adb-toolkit device-info
 *        npx android-adb-toolkit revoke-location com.facebook.katana
 *        npx android-adb-toolkit list-apps
 */
const { execSync } = require('child_process');
const args = process.argv.slice(2);

function adb(cmd) {
  try {
    return execSync(`adb shell ${cmd}`, { encoding: 'utf-8' }).trim();
  } catch(e) {
    return `ERROR: ${e.message}`;
  }
}

const commands = {
  'device-info': () => {
    console.log('\n📱 Device Info\n');
    console.log(`Model:    ${adb("getprop ro.product.model")}`);
    console.log(`Android:  ${adb("getprop ro.build.version.release")}`);
    console.log(`API:      ${adb("getprop ro.build.version.sdk")}`);
    console.log(`Battery:  ${adb("dumpsys battery | grep level | awk '{print $2}'")}`);
    console.log();
  },
  
  'list-apps': () => {
    const apps = adb("pm list packages -3").split('\n').map(l => l.split(':')[1]).filter(Boolean);
    console.log(`\n📦 ${apps.length} user apps\n`);
    apps.slice(0, 20).forEach(a => console.log(`  ${a}`));
    if(apps.length > 20) console.log(`  ... and ${apps.length-20} more\n`);
  },
  
  'revoke-location': (pkg) => {
    if(!pkg) { console.log('Usage: revoke-location <package>'); return; }
    adb(`pm revoke ${pkg} android.permission.ACCESS_FINE_LOCATION`);
    adb(`pm revoke ${pkg} android.permission.ACCESS_COARSE_LOCATION`);
    console.log(`✓ Location revoked from ${pkg}`);
  },
  
  'disable-app': (pkg) => {
    if(!pkg) { console.log('Usage: disable-app <package>'); return; }
    adb(`pm disable-user --user 0 ${pkg}`);
    console.log(`✓ Disabled: ${pkg}`);
  },
};

const cmd = args[0];
if(commands[cmd]) {
  commands[cmd](args[1]);
} else {
  console.log('Available: device-info, list-apps, revoke-location, disable-app');
}
