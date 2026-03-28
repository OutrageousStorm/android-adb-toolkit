#!/usr/bin/env node
/**
 * adb-toolkit CLI — Node.js companion for OutrageousStorm/android-adb-toolkit
 * Install: npm install -g . (from cli/ directory)
 * Usage:   adb-toolkit info
 *          adb-toolkit debloat --profile samsung
 *          adb-toolkit perms --pkg com.facebook.katana
 *          adb-toolkit screenshot
 */
const { execSync, spawn } = require('child_process');
const { program } = require('commander');
const chalk = require('chalk');

function adb(cmd) {
  try {
    return execSync(`adb shell ${cmd}`, { encoding: 'utf8', stdio: ['pipe','pipe','pipe'] }).trim();
  } catch (e) { return ''; }
}

function checkDevice() {
  const out = execSync('adb devices', { encoding: 'utf8' });
  const lines = out.split('\n').filter(l => l.includes('\tdevice'));
  if (!lines.length) {
    console.error(chalk.red('❌ No device connected. Enable USB debugging.'));
    process.exit(1);
  }
}

program
  .name('adb-toolkit')
  .description('Android ADB Toolkit CLI')
  .version('1.0.0');

// ── info ──────────────────────────────────────────────────────────
program.command('info')
  .description('Show device info summary')
  .action(() => {
    checkDevice();
    console.log(chalk.cyan('\n📱 Device Info\n') + '─'.repeat(40));
    const fields = [
      ['Model',    'getprop ro.product.model'],
      ['Brand',    'getprop ro.product.brand'],
      ['Android',  'getprop ro.build.version.release'],
      ['API',      'getprop ro.build.version.sdk'],
      ['Security', 'getprop ro.build.version.security_patch'],
      ['Arch',     'getprop ro.product.cpu.abi'],
      ['Battery',  'dumpsys battery | grep level'],
    ];
    for (const [label, cmd] of fields) {
      const val = adb(cmd).replace(/\n.*/s, '');
      console.log(`  ${chalk.dim(label.padEnd(12))} ${val}`);
    }
    console.log();
  });

// ── screenshot ────────────────────────────────────────────────────
program.command('screenshot')
  .description('Take a screenshot and save locally')
  .option('-o, --output <file>', 'output filename', `screenshot_${Date.now()}.png`)
  .action((opts) => {
    checkDevice();
    console.log(chalk.yellow('📸 Taking screenshot...'));
    execSync(`adb exec-out screencap -p > "${opts.output}"`);
    console.log(chalk.green(`✅ Saved: ${opts.output}`));
  });

// ── perms ─────────────────────────────────────────────────────────
program.command('perms')
  .description('List or revoke dangerous permissions for an app')
  .requiredOption('--pkg <package>', 'Package name')
  .option('--revoke', 'Revoke all dangerous permissions found')
  .action((opts) => {
    checkDevice();
    const dangerous = [
      'ACCESS_FINE_LOCATION','ACCESS_COARSE_LOCATION','READ_CONTACTS',
      'RECORD_AUDIO','CAMERA','READ_SMS','READ_CALL_LOG','GET_ACCOUNTS',
    ];
    console.log(chalk.cyan(`\n🔐 Permissions: ${opts.pkg}\n`));
    const dump = adb(`dumpsys package ${opts.pkg}`);
    const granted = dangerous.filter(p => dump.includes(`android.permission.${p}`) && dump.includes('granted=true'));
    if (!granted.length) {
      console.log(chalk.green('  ✅ No dangerous permissions granted'));
      return;
    }
    for (const p of granted) {
      console.log(`  ⚠️  ${p}`);
      if (opts.revoke) {
        adb(`pm revoke ${opts.pkg} android.permission.${p}`);
        console.log(chalk.green(`     → revoked`));
      }
    }
    if (!opts.revoke) console.log(chalk.dim('\n  Run with --revoke to remove them'));
  });

// ── packages ──────────────────────────────────────────────────────
program.command('packages')
  .description('List installed packages')
  .option('--user', 'User-installed only')
  .option('--filter <keyword>', 'Filter by keyword')
  .action((opts) => {
    checkDevice();
    const flag = opts.user ? '-3' : '';
    const raw = adb(`pm list packages ${flag}`);
    let pkgs = raw.split('\n').map(l => l.replace('package:','').trim()).filter(Boolean);
    if (opts.filter) pkgs = pkgs.filter(p => p.includes(opts.filter));
    console.log(chalk.cyan(`\n📦 ${pkgs.length} packages\n`));
    pkgs.forEach(p => console.log(`  ${p}`));
  });

// ── input ─────────────────────────────────────────────────────────
program.command('type <text>')
  .description('Type text on the device')
  .action((text) => {
    checkDevice();
    adb(`input text "${text.replace(/ /g, '%s')}"`);
    console.log(chalk.green(`✅ Typed: ${text}`));
  });

program.parse();
