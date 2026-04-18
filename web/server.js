import express from 'express';
import { ADB } from 'adb-ts';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const adb = new ADB();

// API endpoints
app.get('/api/devices', async (req, res) => {
    try {
        const devices = await adb.getDevices();
        res.json(devices);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/shell', async (req, res) => {
    const { deviceId, command } = req.body;
    try {
        const device = await adb.getDevice(deviceId);
        const result = await device.shell(command);
        res.json({ output: result });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.get('/api/device/:id/info', async (req, res) => {
    try {
        const device = await adb.getDevice(req.params.id);
        const model = await device.shell('getprop ro.product.model');
        const android = await device.shell('getprop ro.build.version.release');
        const serial = await device.shell('getprop ro.serialno');
        res.json({ model, android, serial });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(8080, () => {
    console.log('ADB Web Toolkit listening on http://localhost:8080');
});
