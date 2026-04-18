#!/usr/bin/env node
/**
 * batch-installer.js -- Bulk install/uninstall APKs via ADB
 * Usage: npx batch-installer install ./apks
 *        npx batch-installer uninstall com.facebook.katana com.instagram.android
 *        npx batch-installer list
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function adb(cmd) {
    try {
        return execSync(`adb shell ${cmd}`, { encoding: 'utf-8' }).trim();
    } catch (e) {
        return '';
    }
}

function main() {
    const [,, cmd, ...args] = process.argv;

    if (!cmd) {
        console.log(`
🔧 ADB Batch Installer

Usage:
  batch-installer install <dir>        Install all APKs from directory
  batch-installer uninstall <pkg...>   Remove packages
  batch-installer list                 List user-installed packages
  batch-installer clear <pkg...>       Clear app data + cache
        `);
        return;
    }

    if (cmd === 'install') {
        const dir = args[0];
        if (!fs.existsSync(dir)) {
            console.error(`Directory not found: ${dir}`);
            return;
        }
        const apks = fs.readdirSync(dir).filter(f => f.endsWith('.apk'));
        console.log(`📲 Installing ${apks.length} APKs...
`);
        let ok = 0;
        apks.forEach((apk, i) => {
            const fullPath = path.join(dir, apk);
            try {
                execSync(`adb install -r "${fullPath}"`, { stdio: 'pipe' });
                console.log(`  ✓ ${apk}`);
                ok++;
            } catch (e) {
                console.log(`  ✗ ${apk}`);
            }
        });
        console.log(`
✅ Installed: ${ok}/${apks.length}`);
    }

    if (cmd === 'uninstall') {
        console.log(`
🗑️  Uninstalling ${args.length} packages...
`);
        args.forEach(pkg => {
            try {
                adb(`pm uninstall -k --user 0 ${pkg}`);
                console.log(`  ✓ ${pkg.split('.').pop()}`);
            } catch (e) {
                console.log(`  ✗ ${pkg}`);
            }
        });
        console.log('
✅ Done');
    }

    if (cmd === 'list') {
        const out = adb('pm list packages -3');
        const pkgs = out.split('
').map(l => l.replace('package:', '')).filter(p => p);
        console.log(`
📱 Installed (${pkgs.length} apps):
`);
        pkgs.forEach(p => console.log(`  ${p}`));
    }

    if (cmd === 'clear') {
        console.log(`
🧹 Clearing data for ${args.length} apps...
`);
        args.forEach(pkg => {
            adb(`pm clear ${pkg}`);
            console.log(`  ✓ ${pkg.split('.').pop()}`);
        });
    }
}

main();
