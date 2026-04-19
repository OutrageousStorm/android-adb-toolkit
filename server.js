const express = require('express');
const { exec } = require('child_process');
const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static('public'));

function adb(cmd) {
  return new Promise((resolve, reject) => {
    exec(`adb shell ${cmd}`, (err, stdout) => {
      resolve(stdout.trim());
    });
  });
}

// Device info endpoint
app.get('/api/device', async (req, res) => {
  const model = await adb("getprop ro.product.model");
  const android = await adb("getprop ro.build.version.release");
  const battery = await adb("dumpsys battery | grep level");
  res.json({ model, android, battery });
});

// Package list endpoint
app.get('/api/packages', async (req, res) => {
  const output = await adb("pm list packages -3");
  const packages = output.split('\n').filter(l => l.startsWith('package:')).map(l => l.substring(8));
  res.json({ packages, count: packages.length });
});

// Screenshot endpoint
app.get('/api/screenshot', (req, res) => {
  exec('adb exec-out screencap -p > /tmp/ss.png && cat /tmp/ss.png', (err, stdout) => {
    res.setHeader('Content-Type', 'image/png');
    res.send(stdout);
  });
});

// Tap command
app.post('/api/tap', async (req, res) => {
  const { x, y } = req.body;
  await adb(`input tap ${x} ${y}`);
  res.json({ ok: true });
});

// Swipe command
app.post('/api/swipe', async (req, res) => {
  const { x1, y1, x2, y2 } = req.body;
  await adb(`input swipe ${x1} ${y1} ${x2} ${y2} 300`);
  res.json({ ok: true });
});

// Install APK
app.post('/api/install', async (req, res) => {
  const { url } = req.body;
  exec(`adb install "${url}"`, (err, stdout) => {
    res.json({ result: stdout, error: err });
  });
});

// List running apps
app.get('/api/running', async (req, res) => {
  const output = await adb("cmd activity get-top-activity");
  res.json({ output });
});

app.listen(PORT, () => {
  console.log(`ADB Server running on http://localhost:${PORT}`);
  console.log('API endpoints:');
  console.log('  GET  /api/device        - Device info');
  console.log('  GET  /api/packages      - Installed packages');
  console.log('  GET  /api/screenshot    - Screenshot');
  console.log('  GET  /api/running       - Top activity');
  console.log('  POST /api/tap           - Tap at coordinates');
  console.log('  POST /api/swipe         - Swipe');
  console.log('  POST /api/install       - Install APK from URL');
});
