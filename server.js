#!/usr/bin/env node
/**
 * server.js -- Enhanced HTTP ADB server with WebSocket support
 * Usage: node server.js [--port 8080] [--host 0.0.0.0]
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PORT = parseInt(process.env.PORT) || 8080;
const HOST = '0.0.0.0';

function adb(cmd) {
  try {
    return execSync(`adb shell ${cmd}`, { encoding: 'utf8' }).trim();
  } catch (e) {
    return `Error: ${e.message}`;
  }
}

const routes = {
  '/api/device': () => JSON.stringify({
    model: adb('getprop ro.product.model'),
    android: adb('getprop ro.build.version.release'),
    build: adb('getprop ro.build.fingerprint'),
    battery: adb('dumpsys battery | grep level | head -1'),
    storage: adb('df -h /data | tail -1'),
  }),

  '/api/packages': () => {
    const pkgs = adb('pm list packages').split('\n');
    return JSON.stringify({ count: pkgs.length, packages: pkgs });
  },

  '/api/screenshot': () => {
    const file = `/tmp/screenshot_${Date.now()}.png`;
    execSync(`adb exec-out screencap -p > ${file}`);
    return fs.readFileSync(file);
  },

  '/api/apps/running': () => {
    const apps = adb('ps -A | grep -v PID');
    return JSON.stringify({ running: apps.split('\n').length });
  },

  '/api/network': () => {
    const wifi = adb('iwconfig wlan0 2>/dev/null || echo N/A');
    const ip = adb('ip addr show wlan0 | grep "inet " | awk "{print $2}"');
    return JSON.stringify({ wifi, ip });
  },
};

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const url = req.url.split('?')[0];
  const handler = routes[url];

  if (handler) {
    try {
      const result = handler();
      res.writeHead(200);
      res.end(typeof result === 'string' ? result : result);
    } catch (e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: e.message }));
    }
  } else {
    // Serve index.html for root
    if (url === '/') {
      res.setHeader('Content-Type', 'text/html');
      const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
      res.writeHead(200);
      res.end(html);
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({ error: 'Not found', available: Object.keys(routes) }));
    }
  }
});

server.listen(PORT, HOST, () => {
  console.log(`🚀 ADB Server running at http://${HOST}:${PORT}`);
  console.log(`Available endpoints: ${Object.keys(routes).join(', ')}`);
});
