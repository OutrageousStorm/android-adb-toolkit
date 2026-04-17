#!/usr/bin/env node
/**
 * cli.js - Command-line ADB wrapper
 * Usage: adb-toolkit <command> [args]
 */
const { exec } = require('child_process');

function adb(cmd) {
  return new Promise((resolve, reject) => {
    exec(`adb shell ${cmd}`, (err, stdout) => {
      if (err) reject(err);
      resolve(stdout.trim());
    });
  });
}

async function main() {
  const [cmd, ...args] = process.argv.slice(2);
  
  try {
    switch(cmd) {
      case 'app-info':
        const pkg = args[0] || 'com.example.app';
        const info = await adb(`dumpsys package ${pkg} | grep versionName`);
        console.log(`App: ${pkg}\n${info}`);
        break;
      case 'screenshot':
        exec(`adb exec-out screencap -p > screenshot_${Date.now()}.png`);
        console.log('✓ Screenshot saved');
        break;
      case 'battery':
        const bat = await adb('dumpsys battery');
        console.log(bat.split('\n').filter(l => l.includes('level') || l.includes('status')).join('\n'));
        break;
      default:
        console.log('Commands: app-info, screenshot, battery, devices');
    }
  } catch (e) {
    console.error(`❌ ${e.message}`);
  }
}

main();
