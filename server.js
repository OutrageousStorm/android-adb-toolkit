// Lightweight Node.js server for web ADB toolkit
const express = require('express');
const { execSync } = require('child_process');
const app = express();

app.use(express.json());
app.use(express.static('web'));

function adb(cmd) {
  try {
    const out = execSync(`adb shell ${cmd}`, { encoding: 'utf8', timeout: 10000 });
    return { stdout: out.trim(), error: null };
  } catch(e) {
    return { stdout: '', error: e.message };
  }
}

app.get('/api/device', (req, res) => {
  res.json({
    model: adb('getprop ro.product.model').stdout,
    android: adb('getprop ro.build.version.release').stdout,
    arch: adb('getprop ro.product.cpu.abi').stdout,
  });
});

app.get('/api/packages', (req, res) => {
  const out = adb('pm list packages').stdout;
  const pkgs = out.split('\n').map(l => l.replace('package:', ''));
  res.json({ count: pkgs.length, packages: pkgs.slice(0, 50) });
});

app.post('/api/cmd', (req, res) => {
  const { cmd } = req.body;
  res.json(adb(cmd));
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`ADB Toolkit listening on :${PORT}`));
