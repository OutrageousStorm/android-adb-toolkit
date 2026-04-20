#!/usr/bin/env node
/**
 * cli.js — Android ADB CLI tool (Node.js)
 * Usage: node cli.js device-info
 *        node cli.js permissions --app com.example.app
 *        node cli.js debloat --list lists/samsung.txt
 */

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

function adb(cmd) {
  try {
    return execSync(`adb shell ${cmd}`, { encoding: "utf8" }).trim();
  } catch (e) {
    return "";
  }
}

const commands = {
  "device-info": () => {
    console.log("\n📱 Device Info");
    console.log("=".repeat(40));
    console.log(`Model:        ${adb("getprop ro.product.model")}`);
    console.log(`Android:      ${adb("getprop ro.build.version.release")}`);
    console.log(`API Level:    ${adb("getprop ro.build.version.sdk")}`);
    console.log(`Build:        ${adb("getprop ro.build.fingerprint")}`);
    console.log(`CPU:          ${adb("getprop ro.product.cpu.abi")}`);
    console.log(`RAM:          ${adb("cat /proc/meminfo | grep MemTotal")}`);
    console.log(`Storage:      ${adb("df -h /data | tail -1")}`);
    console.log(`Bootloader:   ${adb("getprop ro.boot.verifiedbootstate")}`);
    console.log();
  },

  "permissions": (args) => {
    const pkg = args["--app"];
    if (!pkg) {
      console.log("Usage: cli.js permissions --app com.example.app");
      return;
    }
    const perms = adb(`dumpsys package ${pkg} | grep granted=true`);
    console.log(`\n🔐 Permissions for ${pkg}:\n`);
    console.log(perms || "  (none granted)");
    console.log();
  },

  "debloat": (args) => {
    const list = args["--list"];
    if (!list || !fs.existsSync(list)) {
      console.log(`Usage: cli.js debloat --list <file.txt>`);
      return;
    }
    const pkgs = fs.readFileSync(list, "utf8").split("\n")
      .map(l => l.trim())
      .filter(l => l && !l.startsWith("#"));
    
    console.log(`\n🗑️  Debloating ${pkgs.length} packages...\n`);
    let removed = 0, failed = 0;
    pkgs.forEach(pkg => {
      const r = adb(`pm uninstall -k --user 0 ${pkg}`);
      if (r.includes("Success") || r === "") {
        console.log(`  ✓ ${pkg}`);
        removed++;
      } else {
        console.log(`  ✗ ${pkg}`);
        failed++;
      }
    });
    console.log(`\n✅ Removed: ${removed}  ❌ Failed: ${failed}\n`);
  },

  "backup": () => {
    const dir = `backup_${new Date().toISOString().slice(0,10)}`;
    require("child_process").mkdirSync(dir, { recursive: true });
    console.log(`\n📦 Backing up to ${dir}...`);
    
    // Device info
    fs.writeFileSync(`${dir}/device_info.txt`,
      `Model: ${adb("getprop ro.product.model")}\n` +
      `Android: ${adb("getprop ro.build.version.release")}\n` +
      `Build: ${adb("getprop ro.build.fingerprint")}\n`
    );
    console.log(`  ✓ device_info.txt`);

    // Package list
    const pkgs = adb("pm list packages -3");
    fs.writeFileSync(`${dir}/packages.txt`, pkgs);
    console.log(`  ✓ packages.txt (${pkgs.split("\n").length} apps)`);

    console.log(`\n✅ Backup saved to ${dir}/\n`);
  },
};

const args = process.argv.slice(2);
const cmd = args[0];
const opts = {};
for (let i = 1; i < args.length; i += 2) {
  if (args[i].startsWith("--")) {
    opts[args[i]] = args[i + 1];
  }
}

if (!cmd || !commands[cmd]) {
  console.log("Available commands:");
  Object.keys(commands).forEach(c => console.log(`  node cli.js ${c}`));
  process.exit(1);
}

commands[cmd](opts);
