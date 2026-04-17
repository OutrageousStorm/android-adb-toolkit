#!/usr/bin/env node
/**
 * cli.js -- Command-line interface for ADB operations
 * Companion to the web UI for power users who prefer terminal
 * Usage: node cli.js [command] [args]
 */

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

function adb(cmd) {
    try {
        return execSync(`adb shell ${cmd}`, { encoding: "utf-8" });
    } catch (e) {
        return `ERROR: ${e.message}`;
    }
}

function deviceInfo() {
    console.log("\n📱 Device Information");
    console.log("═".repeat(40));
    const fields = {
        "Model": "ro.product.model",
        "Android": "ro.build.version.release",
        "Build": "ro.build.fingerprint",
        "Storage": "df /data | tail -1",
        "Battery": "dumpsys battery | grep level",
    };
    for (const [label, cmd] of Object.entries(fields)) {
        const val = adb(`getprop ${cmd}` || cmd).trim();
        console.log(`  ${label.padEnd(12)} ${val}`);
    }
}

function listApps(userOnly = true) {
    const flag = userOnly ? "-3" : "";
    const out = adb(`pm list packages ${flag}`);
    const apps = out.split("\n")
        .filter(l => l.startsWith("package:"))
        .map(l => l.substring(8))
        .sort();
    console.log(`\n📦 ${apps.length} ${userOnly ? "user" : "all"} packages:`);
    apps.slice(0, 20).forEach(a => console.log(`  ${a}`));
    if (apps.length > 20) console.log(`  ... and ${apps.length - 20} more`);
}

function revokePermission(pkg, perm) {
    const result = adb(`pm revoke ${pkg} ${perm}`);
    console.log(`✓ Revoked ${perm.split(".").pop()} from ${pkg}`);
}

function installApp(apkPath) {
    if (!fs.existsSync(apkPath)) {
        console.log(`❌ File not found: ${apkPath}`);
        return;
    }
    console.log(`📲 Installing ${path.basename(apkPath)}...`);
    try {
        execSync(`adb install "${apkPath}"`);
        console.log("✅ Installed");
    } catch (e) {
        console.log(`❌ ${e.message}`);
    }
}

function screenshot(output = "screenshot.png") {
    console.log(`📸 Taking screenshot...`);
    execSync(`adb exec-out screencap -p > ${output}`);
    console.log(`✅ Saved: ${output}`);
}

function main() {
    const cmd = process.argv[2];
    const args = process.argv.slice(3);

    switch (cmd) {
        case "info":
            deviceInfo();
            break;
        case "apps":
            listApps(!args.includes("--all"));
            break;
        case "revoke":
            if (args.length < 2) {
                console.log("Usage: cli.js revoke <package> <permission>");
                console.log("Example: cli.js revoke com.facebook.katana android.permission.ACCESS_FINE_LOCATION");
                break;
            }
            revokePermission(args[0], args[1]);
            break;
        case "install":
            installApp(args[0] || "app.apk");
            break;
        case "screenshot":
            screenshot(args[0] || "screenshot.png");
            break;
        default:
            console.log(`\n🤖 ADB CLI — Command-line interface\n`);
            console.log("Commands:");
            console.log("  info              Device info snapshot");
            console.log("  apps [--all]      List installed packages");
            console.log("  revoke <pkg> <perm>  Revoke permission");
            console.log("  install <apk>     Install APK file");
            console.log("  screenshot [out]  Take screenshot\n");
    }
}

main();
