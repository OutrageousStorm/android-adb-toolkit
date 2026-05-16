// Android ADB Toolkit Web UI
import express from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const app = express();

app.use(express.static('public'));
app.use(express.json());

const PORT = 3000;

// ADB wrapper
async function adb(cmd) {
  try {
    const { stdout, stderr } = await execAsync(`adb shell ${cmd}`);
    return { ok: true, data: stdout.trim(), error: null };
  } catch (err) {
    return { ok: false, data: null, error: err.message };
  }
}

// Routes
app.get('/api/device', async (req, res) => {
  const model = await adb('getprop ro.product.model');
  const android = await adb('getprop ro.build.version.release');
  const battery = await adb('dumpsys battery | grep level');
  res.json({
    model: model.data,
    android: android.data,
    battery: battery.data,
  });
});

app.post('/api/packages', async (req, res) => {
  const result = await adb('pm list packages -3');
  const packages = result.data.split('\n')
    .filter(l => l.startsWith('package:'))
    .map(l => l.replace('package:', ''));
  res.json({ packages });
});

app.post('/api/revoke', async (req, res) => {
  const { pkg, perm } = req.body;
  const result = await adb(`pm revoke ${pkg} ${perm}`);
  res.json(result);
});

app.post('/api/install', async (req, res) => {
  const { pkg } = req.body;
  const result = await adb(`pm install-existing ${pkg}`);
  res.json(result);
});

app.post('/api/screenshot', async (req, res) => {
  try {
    const { stdout } = await execAsync('adb exec-out screencap -p | base64');
    res.json({ image: `data:image/png;base64,${stdout}` });
  } catch (err) {
    res.json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Android ADB Toolkit running on http://localhost:${PORT}`);
  console.log('Connect device via USB and enable USB debugging.');
});
