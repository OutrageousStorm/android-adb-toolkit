#!/usr/bin/env node
/**
 * device-info.js — Quick device info via ADB (Node.js version)
 * Usage: node device-info.js [--json]
 */
const { execSync } = require('child_process');

function adb(cmd) {
  try {
    return execSync(`adb shell ${cmd}`, { encoding: 'utf-8' }).trim();
  } catch(e) { return ''; }
}

function prop(key) { return adb(`getprop ${key}`); }

function bytes(b) {
  if (b < 1024) return `${b}B`;
  if (b < 1024*1024) return `${(b/1024).toFixed(1)}KB`;
  return `${(b/1024/1024).toFixed(1)}MB`;
}

const json = process.argv.includes('--json');

const info = {
  model: prop('ro.product.model'),
  android: prop('ro.build.version.release'),
  sdk: prop('ro.build.version.sdk'),
  arch: prop('ro.product.cpu.abi'),
  brand: prop('ro.product.brand'),
  device: prop('ro.product.device'),
  security_patch: prop('ro.build.version.security_patch'),
  build_fingerprint: prop('ro.build.fingerprint'),
};

if (json) {
  console.log(JSON.stringify(info, null, 2));
} else {
  console.log('\n📱 Android Device Info\n');
  Object.entries(info).forEach(([k, v]) => {
    console.log(`  ${k.padEnd(20)} ${v || '—'}`);
  });
  console.log();
}
