#!/usr/bin/env node
/**
 * ADB Quick CLI — command-line tool for common ADB tasks
 * Usage: node cli.js [command] [options]
 * Commands: info, apps, perms, debloat, screenshot, record, wifi
 */

const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");

function adb(cmd) {
    return new Promise((res, rej) => {
        exec(`adb shell ${cmd}`, (err, stdout) => {
            if (err) rej(err);
            else res(stdout.trim());
        });
    });
}

const commands = {
    async info() {
        console.log("📱 Device Info");
        console.log("─".repeat(40));
        const model = await adb("getprop ro.product.model");
        const android = await adb("getprop ro.build.version.release");
        const api = await adb("getprop ro.build.version.sdk");
        const battery = await adb("dumpsys battery | grep level");
        console.log(`Model:    ${model}`);
        console.log(`Android:  ${android} (API ${api})`);
        console.log(`Battery:  ${battery}`);
    },

    async apps() {
        console.log("📦 User-Installed Apps");
        const out = await adb("pm list packages -3");
        const apps = out.split("\n").filter(l => l.startsWith("package:"));
        console.log(`Found: ${apps.length}\n`);
        apps.forEach(a => console.log(`  ${a.split(":")[1]}`));
    },

    async screenshot() {
        const file = `screenshot_${Date.now()}.png`;
        exec(`adb exec-out screencap -p > ${file}`, (err) => {
            if (!err) console.log(`✅ Screenshot: ${file}`);
            else console.error("❌ Failed");
        });
    },

    async wifi() {
        console.log("📡 WiFi QR Code — scan to connect");
        // Requires qrencode or similar
        const ssid = await adb("dumpsys wifi | grep SSID");
        console.log(ssid);
    },

    async help() {
        console.log(`
ADB Quick CLI
Usage: node cli.js [command]

Commands:
  info        Show device info (model, Android, battery)
  apps        List installed user apps
  screenshot  Take a screenshot
  wifi        Show WiFi info
  help        This message
        `);
    }
};

const cmd = process.argv[2] || "help";
if (commands[cmd]) {
    commands[cmd]().catch(e => console.error("Error:", e.message));
} else {
    console.error(`Unknown command: ${cmd}`);
    commands.help();
}
