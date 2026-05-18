#!/usr/bin/env node
/**
 * event-parser.js -- Parse and filter Android input events from /dev/input
 * Usage: node event-parser.js --filter TYPE_TOUCH
 *        adb shell getevent | node event-parser.js --live
 */

const fs = require('fs');
const readline = require('readline');

const EVENT_CODES = {
    'EV_SYN': 0x00,
    'EV_KEY': 0x01,
    'EV_REL': 0x02,
    'EV_ABS': 0x03,
    'EV_MSC': 0x04,
    'EV_SW': 0x05,
    'EV_LED': 0x11,
    'EV_SND': 0x12,
    'EV_REP': 0x14,
    'EV_FF': 0x15,
    'EV_PWR': 0x16,
};

const ABS_CODES = {
    'ABS_X': 0x00,
    'ABS_Y': 0x01,
    'ABS_Z': 0x02,
    'ABS_MT_POSITION_X': 0x35,
    'ABS_MT_POSITION_Y': 0x36,
    'ABS_MT_PRESSURE': 0x3a,
    'ABS_MT_TRACKING_ID': 0x39,
};

class EventParser {
    constructor(filter = null) {
        this.filter = filter;
        this.events = [];
        this.touches = [];
    }

    parseLine(line) {
        // Format: /dev/input/event0: 0003 0035 0258  -> EV_ABS ABS_MT_POSITION_X 600
        const match = line.match(/\/dev\/input\/event(\d+):\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)/i);
        if (!match) return null;

        const [, device, type, code, value] = match;
        const typeHex = parseInt(type, 16);
        const codeHex = parseInt(code, 16);
        const valueHex = parseInt(value, 16);

        let eventType = Object.entries(EVENT_CODES).find(([_, v]) => v === typeHex)?.[0] || `0x${type}`;
        let codeName = codeHex >= 0x35 && codeHex <= 0x3f 
            ? Object.entries(ABS_CODES).find(([_, v]) => v === codeHex)?.[0] || `0x${code}`
            : `0x${code}`;

        return {
            device: parseInt(device),
            type: eventType,
            typeHex,
            code: codeName,
            codeHex,
            value: valueHex,
            timestamp: new Date().toISOString()
        };
    }

    processEvent(event) {
        if (!event) return;
        if (this.filter && !event.type.includes(this.filter.toUpperCase())) return;

        this.events.push(event);

        // Track touch events
        if (event.type === 'EV_ABS') {
            if (event.code.includes('POSITION_X')) this.lastX = event.value;
            if (event.code.includes('POSITION_Y')) this.lastY = event.value;
            if (event.code.includes('TRACKING_ID')) {
                if (event.value !== 0xffffffff) {
                    this.touches.push({ x: this.lastX, y: this.lastY, id: event.value, time: event.timestamp });
                }
            }
        }

        console.log(`${event.timestamp} | ${event.type.padEnd(10)} | ${event.code.padEnd(25)} | ${event.value}`);
    }

    printTouchSummary() {
        if (this.touches.length === 0) {
            console.log('No touch events detected');
            return;
        }
        console.log(`
📊 Touch Summary (${this.touches.length} events):`);
        this.touches.forEach((t, i) => {
            console.log(`  ${i+1}. (${t.x}, ${t.y}) ID: ${t.id}`);
        });
    }
}

// CLI
const args = process.argv.slice(2);
const filter = args.includes('--filter') ? args[args.indexOf('--filter') + 1] : null;
const isLive = args.includes('--live');

const parser = new EventParser(filter);

if (isLive) {
    console.log('🔴 Listening for events (press Ctrl+C to stop)...');
    const proc = require('child_process').spawn('adb', ['shell', 'getevent']);
    const rl = readline.createInterface({ input: proc.stdout });
    rl.on('line', line => parser.processEvent(parser.parseLine(line)));
    process.on('SIGINT', () => {
        parser.printTouchSummary();
        process.exit(0);
    });
} else {
    const rl = readline.createInterface({ input: process.stdin });
    rl.on('line', line => parser.processEvent(parser.parseLine(line)));
    rl.on('close', () => parser.printTouchSummary());
}
