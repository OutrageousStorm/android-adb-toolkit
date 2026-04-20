#!/usr/bin/env node
/**
 * server.js -- Express.js web server for ADB control
 * npm install express cors
 * node server.js
 * Open http://localhost:3000
 */

const express = require("express");
const { exec } = require("child_process");
const { promisify } = require("util");
const path = require("path");

const execAsync = promisify(exec);
const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname)));

async function adb(cmd) {
    try {
        const { stdout } = await execAsync(`adb shell ${cmd}`);
        return stdout.trim();
    } catch (e) {
        return `Error: ${e.message}`;
    }
}

// API endpoints
app.post("/api/exec", async (req, res) => {
    const { command } = req.body;
    const result = await adb(command);
    res.json({ command, result });
});

app.get("/api/devices", async (req, res) => {
    try {
        const { stdout } = await execAsync("adb devices");
        const devices = stdout.split("\n").slice(1)
            .filter(l => l.includes("device"))
            .map(l => l.split("\t")[0]);
        res.json({ devices });
    } catch (e) {
        res.json({ error: e.message });
    }
});

app.get("/api/info", async (req, res) => {
    const model = await adb("getprop ro.product.model");
    const android = await adb("getprop ro.build.version.release");
    const storage = await adb("df -h /data | tail -1 | awk '{print $2, $3}'");
    res.json({ model, android, storage });
});

app.post("/api/install", async (req, res) => {
    const { apkPath } = req.body;
    const result = await adb(`pm install -r "${apkPath}"`);
    res.json({ status: result.includes("Success") ? "ok" : "failed", result });
});

app.post("/api/uninstall", async (req, res) => {
    const { pkg } = req.body;
    const result = await adb(`pm uninstall -k --user 0 ${pkg}`);
    res.json({ status: result.includes("Success") ? "ok" : "failed", result });
});

app.get("/api/packages", async (req, res) => {
    const result = await adb("pm list packages -3");
    const packages = result.split("\n")
        .map(l => l.replace("package:", ""))
        .filter(l => l);
    res.json({ count: packages.length, packages: packages.slice(0, 50) });
});

app.listen(PORT, () => {
    console.log(`🖥️  ADB Web Server running at http://localhost:${PORT}`);
    console.log("   Endpoints: /api/exec, /api/devices, /api/info, /api/packages, /api/install, /api/uninstall");
});
