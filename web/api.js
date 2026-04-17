/**
 * api.js -- ADB WebUI API wrapper
 * Communicates with adb-server backend
 */

const ADB_URL = 'http://localhost:5037/api';

async function call(method, params = {}) {
  try {
    const res = await fetch(ADB_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ method, params })
    });
    return await res.json();
  } catch (e) {
    console.error('ADB API error:', e);
    return { error: e.message };
  }
}

async function getDevices() {
  return call('devices');
}

async function getPackages(device) {
  return call('list_packages', { device });
}

async function uninstallPackage(device, pkg) {
  return call('uninstall', { device, package: pkg });
}

async function installAPK(device, apk_path) {
  return call('install', { device, apk: apk_path });
}

async function getDeviceInfo(device) {
  return call('device_info', { device });
}

async function rebootDevice(device, mode = 'system') {
  return call('reboot', { device, mode });
}

export { getDevices, getPackages, uninstallPackage, installAPK, getDeviceInfo, rebootDevice };
