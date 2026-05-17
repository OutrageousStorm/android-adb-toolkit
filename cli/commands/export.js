/**
 * export.js — Export device state as JSON/CSV
 * Usage: adb-toolkit export [--format json|csv] [--output file.json]
 */
const { execSync } = require('child_process');
const fs = require('fs');

function adb(cmd) {
  try {
    return execSync(`adb shell ${cmd}`, { encoding: 'utf8', stdio: ['pipe','pipe','pipe'] }).trim();
  } catch { return ''; }
}

async function exportDevice(format = 'json', output = null) {
  const data = {
    device: {
      model: adb('getprop ro.product.model'),
      android: adb('getprop ro.build.version.release'),
      api: adb('getprop ro.build.version.sdk'),
      security_patch: adb('getprop ro.build.version.security_patch'),
    },
    packages: adb('pm list packages').split('\n').map(l => l.replace('package:', '')).filter(Boolean),
    permissions: adb('pm list permissions').split('\n').filter(Boolean),
    features: adb('pm list features').split('\n').filter(Boolean),
    battery: adb('dumpsys battery | grep -E "level|temperature|status"').split('\n').filter(Boolean),
  };

  const formatted = format === 'csv' ? convertToCSV(data) : JSON.stringify(data, null, 2);
  
  if (output) {
    fs.writeFileSync(output, formatted);
    console.log(`✅ Exported to ${output}`);
  } else {
    console.log(formatted);
  }
}

function convertToCSV(data) {
  const lines = [];
  lines.push('Category,Key,Value');
  for (const [cat, obj] of Object.entries(data)) {
    if (typeof obj === 'object' && !Array.isArray(obj)) {
      for (const [k, v] of Object.entries(obj)) {
        lines.push(`${cat},"${k}","${v}"`);
      }
    }
  }
  return lines.join('\n');
}

module.exports = { exportDevice };
