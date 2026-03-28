const http = require('http');
const { exec } = require('child_process');
const url = require('url');
const qs = require('querystring');

const PORT = 3000;

function adb(cmd) {
    return new Promise((resolve, reject) => {
        exec(`adb shell ${cmd}`, (e, out, err) => {
            if (e) reject(err || e.message);
            else resolve(out.trim());
        });
    });
}

const server = http.createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');

    const pathname = url.parse(req.url).pathname;
    const query = qs.parse(url.parse(req.url).query);

    try {
        if (pathname === '/api/device-info') {
            const model = await adb("getprop ro.product.model");
            const version = await adb("getprop ro.build.version.release");
            res.end(JSON.stringify({ model, version }, null, 2));
        } else if (pathname === '/api/packages') {
            const out = await adb("pm list packages -3");
            const packages = out.split('\n').map(l => l.split(':')[1]).filter(p => p);
            res.end(JSON.stringify({ packages, count: packages.length }, null, 2));
        } else if (pathname === '/api/battery') {
            const out = await adb("dumpsys battery");
            const level = out.match(/level: (\d+)/)?.[1];
            const status = out.match(/status: (\w+)/)?.[1];
            res.end(JSON.stringify({ level, status }, null, 2));
        } else {
            res.statusCode = 404;
            res.end(JSON.stringify({ error: 'Not found' }));
        }
    } catch (error) {
        res.statusCode = 500;
        res.end(JSON.stringify({ error: error.toString() }));
    }
});

server.listen(PORT, () => {
    console.log(`ADB server on http://localhost:${PORT}`);
});
