#!/usr/bin/env node
/**
 * gesture_recorder.js -- Record touch gestures and replay them
 * Usage: node gesture_recorder.js --record output.json
 *        node gesture_recorder.js --replay output.json [--repeat 5]
 */
const { exec } = require('child_process');
const fs = require('fs');
const readline = require('readline');

function adb(cmd) {
    return new Promise((resolve, reject) => {
        exec(`adb shell ${cmd}`, (err, stdout, stderr) => {
            resolve(stdout.trim());
        });
    });
}

async function captureGestures(outputFile) {
    console.log('🎬 Gesture Recorder');
    console.log('==================');
    console.log('Recording touch events. Press Ctrl+C to stop.\n');
    
    const gestures = [];
    let recording = false;
    
    // Start getevent monitoring
    const proc = require('child_process').spawn('adb', ['shell', 'getevent']);
    
    const rl = readline.createInterface({
        input: proc.stdout,
        output: process.stdout,
        terminal: false
    });

    const touchStart = Date.now();
    let lastX = 0, lastY = 0;

    rl.on('line', (line) => {
        // Parse getevent output for touch events
        // /dev/input/eventX: type ABS_X value 540
        if (line.includes('ABS_X')) {
            const match = line.match(/value\s+(\d+)/);
            if (match) lastX = parseInt(match[1]);
        } else if (line.includes('ABS_Y')) {
            const match = line.match(/value\s+(\d+)/);
            if (match) lastY = parseInt(match[1]);
        } else if (line.includes('BTN_TOUCH') && line.includes('DOWN')) {
            gestures.push({
                action: 'touch_down',
                x: lastX,
                y: lastY,
                time: Date.now() - touchStart
            });
            console.log(`📍 Touch down: (${lastX}, ${lastY})`);
        } else if (line.includes('BTN_TOUCH') && line.includes('UP')) {
            gestures.push({
                action: 'touch_up',
                x: lastX,
                y: lastY,
                time: Date.now() - touchStart
            });
            console.log(`📍 Touch up: (${lastX}, ${lastY})`);
        }
    });

    process.on('SIGINT', () => {
        proc.kill();
        rl.close();
        
        // Post-process: convert to taps and swipes
        const processed = processGestures(gestures);
        fs.writeFileSync(outputFile, JSON.stringify(processed, null, 2));
        console.log(`\n✅ Saved ${processed.length} gestures to ${outputFile}`);
        process.exit(0);
    });
}

function processGestures(events) {
    const result = [];
    let i = 0;
    while (i < events.length) {
        if (events[i].action === 'touch_down') {
            const startX = events[i].x;
            const startY = events[i].y;
            const startTime = events[i].time;

            // Find matching touch_up
            let j = i + 1;
            while (j < events.length && events[j].action === 'touch_down') j++;

            if (j < events.length && events[j].action === 'touch_up') {
                const endX = events[j].x;
                const endY = events[j].y;
                const endTime = events[j].time;
                const duration = endTime - startTime;

                if (Math.abs(startX - endX) < 50 && Math.abs(startY - endY) < 50) {
                    // Tap
                    result.push({
                        action: 'tap',
                        x: startX,
                        y: startY,
                        delay: 0.3
                    });
                } else {
                    // Swipe
                    result.push({
                        action: 'swipe',
                        x1: startX,
                        y1: startY,
                        x2: endX,
                        y2: endY,
                        duration: Math.min(duration, 500),
                        delay: 0.2
                    });
                }
                i = j + 1;
            } else {
                i++;
            }
        } else {
            i++;
        }
    }
    return result;
}

async function replayGestures(inputFile, repeat = 1) {
    const gestures = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
    console.log(`▶️  Replaying ${gestures.length} gestures (${repeat} times)\n`);

    for (let r = 0; r < repeat; r++) {
        if (repeat > 1) console.log(`Run ${r+1}/${repeat}`);
        
        for (let i = 0; i < gestures.length; i++) {
            const g = gestures[i];
            if (g.action === 'tap') {
                await adb(`input tap ${g.x} ${g.y}`);
                console.log(`  [${i+1}] tap (${g.x}, ${g.y})`);
            } else if (g.action === 'swipe') {
                await adb(`input swipe ${g.x1} ${g.y1} ${g.x2} ${g.y2} ${g.duration}`);
                console.log(`  [${i+1}] swipe (${g.x1},${g.y1}) → (${g.x2},${g.y2})`);
            }
            if (g.delay) await new Promise(r => setTimeout(r, g.delay * 1000));
        }
    }
    console.log('\n✅ Replay complete.');
}

// Main
const args = process.argv.slice(2);
if (args[0] === '--record') {
    captureGestures(args[1] || 'gestures.json');
} else if (args[0] === '--replay') {
    const repeat = args[2] === '--repeat' ? parseInt(args[3]) : 1;
    replayGestures(args[1] || 'gestures.json', repeat);
} else {
    console.log('Usage:');
    console.log('  node gesture_recorder.js --record output.json');
    console.log('  node gesture_recorder.js --replay output.json [--repeat 5]');
}
