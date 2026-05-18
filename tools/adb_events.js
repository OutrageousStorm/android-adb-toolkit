#!/usr/bin/env node
/**
 * adb_events.js -- Real-time Android input event monitor
 * Shows all touch, key, and sensor events in real time.
 * Usage: node adb_events.js [--filter touch|key|sensor] [--device serial]
 */

const { exec } = require('child_process');
const readline = require('readline');

function runAdb(cmd) {
  return new Promise((resolve, reject) => {
    exec(`adb shell ${cmd}`, (err, stdout, stderr) => {
      resolve(stdout || stderr);
    });
  });
}

class EventMonitor {
  constructor(filter = null, device = null) {
    this.filter = filter;
    this.device = device || '';
    this.deviceFlag = device ? `-s ${device}` : '';
    this.events = [];
  }

  async start() {
    console.log('\n📱 Android Event Monitor');
    console.log('Filter:', this.filter || 'all');
    console.log('Press Ctrl+C to stop\n');

    // Check device
    let devices = await runAdb('adb devices');
    if (!devices.includes('device')) {
      console.log('❌ No device connected.');
      return;
    }

    // Monitor input events
    const proc = require('child_process').spawn('adb', [
      'shell',
      'getevent'
    ]);

    let lineBuffer = '';
    proc.stdout.on('data', (data) => {
      lineBuffer += data.toString();
      const lines = lineBuffer.split('\n');
      lineBuffer = lines.pop();

      lines.forEach(line => {
        this.parseEvent(line);
      });
    });

    proc.stderr.on('data', (data) => {
      // ignore
    });

    process.on('SIGINT', () => {
      proc.kill();
      console.log('\n✅ Stopped.');
      process.exit(0);
    });
  }

  parseEvent(line) {
    // getevent output: /dev/input/eventX: type code value
    const match = line.match(/\/dev\/input\/event\d+: ([A-F0-9]+) ([A-F0-9]+) ([A-F0-9]+)/);
    if (!match) return;

    const type = parseInt(match[1], 16);
    const code = parseInt(match[2], 16);
    const value = parseInt(match[3], 16);

    let typeStr = 'unknown';
    let eventStr = '';

    // EV_KEY = 0x01
    if (type === 0x01) {
      if (!this.filter || this.filter === 'key') {
        typeStr = 'KEY';
        const keyNames = { 272: 'TOUCH', 330: 'TOUCH_MAJOR', 325: 'PRESSURE' };
        eventStr = `${keyNames[code] || code} = ${value}`;
        console.log(`[${typeStr}] ${eventStr}`);
      }
    }
    // EV_ABS = 0x03 (touch coordinates)
    else if (type === 0x03) {
      if (!this.filter || this.filter === 'touch') {
        typeStr = 'TOUCH';
        const axisNames = { 0: 'X', 1: 'Y', 53: 'TRACKING_ID', 58: 'PRESSURE' };
        eventStr = `${axisNames[code] || code} = ${value}`;
        console.log(`[${typeStr}] ${eventStr}`);
      }
    }
    // EV_SYN = 0x00 (sync)
    else if (type === 0x00 && code === 0) {
      // Sync marker
    }
  }
}

// CLI
const args = process.argv.slice(2);
let filter = null, device = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--filter') filter = args[++i];
  if (args[i] === '--device') device = args[++i];
}

const monitor = new EventMonitor(filter, device);
monitor.start().catch(err => console.error(err));
