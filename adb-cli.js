#!/usr/bin/env node
/**
 * adb-cli.js -- Command-line ADB toolkit
 * Usage: node adb-cli.js [command] [options]
 *        npx adb-cli info
 *        npx adb-cli revoke --app com.facebook.katana --perms LOCATION
 *        npx adb-cli debloat --file samsung.txt --dry-run
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function adb(cmd) {
    try {
        return execSync(`adb shell ${cmd}`, { encoding: 'utf8' }).trim();
    } catch (e) {
        return '';
    }
}

const commands = {
    info: () => {
        console.log('
📱 Device Info
');
        const props = [
            ['Model', 'ro.product.model'],
            ['Brand', 'ro.product.brand'],
            ['Android', 'ro.build.version.release'],
            ['API', 'ro.build.version.sdk'],
            ['ROM', 'ro.build.fingerprint'],
            ['Security Patch', 'ro.build.version.security_patch'],
        ];
        props.forEach(([label, prop]) => {
            const val = adb(`getprop ${prop}`);
            console.log(`  ${label.padEnd(16)} ${val}`);
        });
        console.log();
    },

    revoke: (opts) => {
        const pkg = opts.app || process.argv[process.argv.indexOf('--app') + 1];
        const perms = (opts.perms || 'LOCATION,CONTACTS,CAMERA').split(',');
        console.log(`
🔐 Revoking from ${pkg}
`);
        perms.forEach(perm => {
            const perm_full = `android.permission.${perm.toUpperCase()}`;
            adb(`pm revoke ${pkg} ${perm_full}`);
            console.log(`  ✓ ${perm}`);
        });
        console.log();
    },

    debloat: (opts) => {
        const file = opts.file || process.argv[process.argv.indexOf('--file') + 1];
        const dryRun = opts['dry-run'] || process.argv.includes('--dry-run');
        if (!file || !fs.existsSync(file)) {
            console.log(`❌ File not found: ${file}`);
            return;
        }
        const pkgs = fs.readFileSync(file, 'utf8')
            .split('
')
            .map(l => l.trim())
            .filter(l => l && !l.startsWith('#'));
        console.log(`
🗑️  Debloating (${pkgs.length} packages)
`);
        pkgs.forEach(pkg => {
            if (dryRun) {
                console.log(`  [DRY] pm uninstall -k --user 0 ${pkg}`);
            } else {
                const result = adb(`pm uninstall -k --user 0 ${pkg}`);
                console.log(`  ${result.includes('Success') ? '✓' : '✗'} ${pkg}`);
            }
        });
        console.log();
    },

    install: (opts) => {
        const dir = opts.dir || process.argv[process.argv.indexOf('--dir') + 1] || '.';
        const apks = fs.readdirSync(dir).filter(f => f.endsWith('.apk'));
        console.log(`
📲 Installing ${apks.length} APKs from ${dir}
`);
        apks.forEach(apk => {
            const result = adb(`install -r "${path.join(dir, apk)}"`);
            console.log(`  ${result.includes('Success') ? '✓' : '✗'} ${apk}`);
        });
        console.log();
    },

    list: () => {
        const out = adb('pm list packages -3');
        const pkgs = out.split('
').filter(l => l.startsWith('package:'));
        console.log(`
📦 ${pkgs.length} User Apps
`);
        pkgs.forEach((p, i) => {
            if (i < 20) console.log(`  ${p.replace('package:', '')}`);
        });
        if (pkgs.length > 20) console.log(`  ... and ${pkgs.length - 20} more
`);
    },

    help: () => {
        console.log(`
🛠️  ADB CLI Toolkit

Commands:
  info                  Show device info
  revoke [opts]         Revoke permissions from app
                        --app <pkg> --perms LOCATION,CONTACTS,CAMERA
  debloat [opts]        Remove packages from list file
                        --file samsung.txt [--dry-run]
  install [opts]        Batch install APKs
                        --dir ./apks
  list                  List all user-installed apps
  help                  Show this help

Examples:
  node adb-cli.js info
  node adb-cli.js revoke --app com.facebook.katana --perms LOCATION
  node adb-cli.js debloat --file samsung.txt --dry-run
        `);
    }
};

const cmd = process.argv[2] || 'help';
const opts = {};
for (let i = 3; i < process.argv.length; i += 2) {
    if (process.argv[i].startsWith('--')) {
        opts[process.argv[i].slice(2)] = process.argv[i + 1];
    }
}

if (commands[cmd]) {
    commands[cmd](opts);
} else {
    console.log(`Unknown command: ${cmd}`);
    commands.help();
}
