// Main app logic for web ADB toolkit
const devices = new Map();

async function listDevices() {
    try {
        const res = await fetch('/api/devices');
        const data = await res.json();
        updateDeviceList(data);
        return data;
    } catch (e) {
        console.error('Failed to list devices:', e);
        return [];
    }
}

function updateDeviceList(devList) {
    const el = document.getElementById('device-list');
    el.innerHTML = devList.map(d => `
        <div class="device-item" onclick="selectDevice('${d.serial}')">
            <b>${d.model}</b> (${d.android})
            <small>${d.serial}</small>
        </div>
    `).join('');
}

async function executeCommand(cmd) {
    const device = document.getElementById('selected-device').value;
    if (!device) { alert('Select a device'); return; }
    
    try {
        const res = await fetch('/api/exec', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device, command: cmd })
        });
        const data = await res.json();
        document.getElementById('output').textContent = data.output || data.error || 'No output';
    } catch (e) {
        document.getElementById('output').textContent = 'Error: ' + e.message;
    }
}

// Auto-refresh devices every 5 seconds
setInterval(listDevices, 5000);
listDevices();
