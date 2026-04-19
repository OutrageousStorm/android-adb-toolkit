#!/usr/bin/env node
/**
 * cli.js -- ADB CLI wrapper with interactive menus
 * Usage: node cli.js [command]
 * Commands: info, apps, debloat, backup, restore, network
 */

const { exec } = require("child_process");
const readline = require("readline");

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

function adb(cmd) {
  return new Promise((resolve) => {
    exec(`adb shell ${cmd}`, { maxBuffer: 10 * 1024 * 1024 }, (err, stdout) => {
      resolve(stdout.trim());
    });
  });
}

async function deviceInfo() {
  console.log("\n📱 Device Info");
  console.log("=" .repeat(40));
  console.log("Model:  " + await adb("getprop ro.product.model"));
  console.log("Android:" + await adb("getprop ro.build.version.release"));
  console.log("Build:  " + await adb("getprop ro.build.fingerprint"));
  console.log("CPU:    " + await adb("getprop ro.product.cpu.abi"));
  console.log("RAM:    " + await adb("cat /proc/meminfo | grep MemTotal"));
}

async function listApps() {
  console.log("\n📦 User-installed Apps");
  const output = await adb("pm list packages -3");
  const apps = output.split("\n").map(l => l.replace("package:", "")).sort();
  apps.forEach((app, i) => {
    if (i < 20) console.log(`  ${i+1}. ${app}`);
  });
  if (apps.length > 20) console.log(`  ... and ${apps.length - 20} more`);
}

async function quickDebloat() {
  console.log("\n🗑️  Quick Debloat (social + ad apps)");
  const bloat = [
    "com.facebook.katana",
    "com.instagram.android",
    "com.twitter.android",
    "com.snapchat.android",
  ];
  for (const app of bloat) {
    const result = await adb(`pm uninstall -k --user 0 ${app}`);
    const status = result.includes("Success") ? "✓" : "—";
    console.log(`  ${status} ${app}`);
  }
}

async function menu() {
  console.log("\n🤖 ADB CLI Tool");
  console.log("1) Device Info");
  console.log("2) List Apps");
  console.log("3) Quick Debloat");
  console.log("4) Exit");
  rl.question("Pick: ", async (choice) => {
    switch (choice) {
      case "1": await deviceInfo(); break;
      case "2": await listApps(); break;
      case "3": await quickDebloat(); break;
      case "4": rl.close(); return;
    }
    menu();
  });
}

(async () => {
  const args = process.argv.slice(2);
  if (args.length > 0) {
    switch (args[0]) {
      case "info": await deviceInfo(); break;
      case "apps": await listApps(); break;
      case "debloat": await quickDebloat(); break;
      default: console.log("Unknown command: " + args[0]);
    }
  } else {
    menu();
  }
})();
