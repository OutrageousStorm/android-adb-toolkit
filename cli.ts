/**
 * cli.ts - ADB TypeScript CLI Tool
 * Usage: ts-node cli.ts info
 */

import { execSync } from 'child_process';

const adb = (cmd: string): string => {
    return execSync(`adb shell ${cmd}`, { encoding: 'utf-8' }).trim();
};

const commands: { [key: string]: (args: string[]) => void } = {
    info: () => {
        console.log('Device Info:');
        console.log(`  Model: ${adb("getprop ro.product.model")}`);
        console.log(`  Android: ${adb("getprop ro.build.version.release")}`);
        console.log(`  API: ${adb("getprop ro.build.version.sdk")}`);
        console.log(`  RAM: ${adb("cat /proc/meminfo | grep MemTotal")}`);
    },
    
    screenshot: (args: string[]) => {
        const out = args[0] || 'screenshot.png';
        console.log('Capturing...');
        execSync(`adb exec-out screencap -p > ${out}`);
        console.log(`Saved to ${out}`);
    },
    
    install: (args: string[]) => {
        console.log(`Installing ${args[0]}...`);
        execSync(`adb install -r "${args[0]}"`);
    },
    
    list_apps: () => {
        const apps = adb('pm list packages -3').split('\n');
        console.log(`Found ${apps.length} apps`);
        apps.forEach((a, i) => console.log(`  ${i+1}. ${a.replace('package:', '')}`));
    },
};

const cmd = process.argv[2] || 'info';
(commands[cmd] || commands.info)(process.argv.slice(3));
