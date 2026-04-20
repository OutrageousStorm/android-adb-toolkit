#!/usr/bin/env node
/**
 * adb-server.js -- REST API wrapper for ADB commands
 * Usage: node adb-server.js --port 3000
 * API: GET /api/deviceinfo | /api/packages | /api/shell?cmd=...
 */
const http = require('http');
const { execSync } = require('child_process');
const url = require('url');

const PORT = process.argv[2] === '--port' ? parseInt(process.argv[3]) : 3000;

function adb(cmd) {
    try {
        return execSync(`adb shell ${cmd}`, { encoding: 'utf8' }).trim();
    } catch(e) {
        return `ERROR: ${e.message}`;
    }
}

function deviceInfo() {
    return {
        model: adb('getprop ro.product.model'),
        android: adb('getprop ro.build.version.release'),
        device: adb('getprop ro.product.device'),
        cpu: adb('getprop ro.product.cpu.abi'),
    };
}

function listPackages() {
    const out = adb('pm list packages -3');
    return out.split('\n').filter(l => l).map(l => l.replace('package:', ''));
}

const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');

    const pathname = url.parse(req.url).pathname;
    const query = url.parse(req.url, true).query;

    if (pathname === '/api/deviceinfo') {
        res.writeHead(200);
        res.end(JSON.stringify(deviceInfo(), null, 2));
    } else if (pathname === '/api/packages') {
        res.writeHead(200);
        res.end(JSON.stringify({ packages: listPackages() }, null, 2));
    } else if (pathname === '/api/shell') {
        const cmd = query.cmd || 'echo "usage: /api/shell?cmd=..."';
        res.writeHead(200);
        res.end(JSON.stringify({ command: cmd, output: adb(cmd) }, null, 2));
    } else {
        res.writeHead(404);
        res.end(JSON.stringify({ error: 'Not found' }));
    }
});

server.listen(PORT, () => {
    console.log(`\n📱 ADB REST Server`);
    console.log(`Listening on http://localhost:${PORT}`);
    console.log(`\nEndpoints:`);
    console.log(`  GET /api/deviceinfo`);
    console.log(`  GET /api/packages`);
    console.log(`  GET /api/shell?cmd=<command>`);
    console.log();
});
