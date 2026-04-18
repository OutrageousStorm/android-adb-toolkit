#!/usr/bin/env python3
"""
adb-cli.py -- Command-line companion to web toolkit
Quick access to common ADB operations without the web UI
Usage: python3 adb-cli.py [command] [args...]
"""
import subprocess, sys, argparse

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip(), r.returncode

class ADBCLI:
    def info(self):
        model, _ = adb("getprop ro.product.model")
        android, _ = adb("getprop ro.build.version.release")
        cpu, _ = adb("getprop ro.product.cpu.abi")
        battery, _ = adb("dumpsys battery | grep 'level:' | grep -oE '[0-9]+'")
        print(f"Model:   {model}")
        print(f"Android: {android}")
        print(f"CPU:     {cpu}")
        print(f"Battery: {battery}%")

    def apps(self, filter_kw=None):
        out, _ = adb("pm list packages -3")
        pkgs = [l.split(":")[1] for l in out.splitlines() if l.startswith("package:")]
        if filter_kw:
            pkgs = [p for p in pkgs if filter_kw.lower() in p.lower()]
        for p in pkgs[:20]:
            print(p)
        if len(pkgs) > 20:
            print(f"... and {len(pkgs)-20} more (use --filter to narrow)")

    def uninstall(self, pkg):
        out, code = adb(f"pm uninstall -k --user 0 {pkg}")
        print(f"{'✓' if code == 0 else '✗'} {pkg}: {out[:50]}")

    def revoke(self, pkg, perm):
        out, code = adb(f"pm revoke {pkg} android.permission.{perm}")
        print(f"{'✓' if code == 0 else '✗'} revoked {perm} from {pkg}")

    def screenshot(self, path="/tmp/screen.png"):
        subprocess.run(f"adb exec-out screencap -p > {path}", shell=True)
        print(f"✓ Screenshot saved to {path}")

    def reboot(self, mode='system'):
        subprocess.Popen(f"adb reboot {mode}", shell=True)
        print(f"Rebooting to {mode}...")

def main():
    cli = ADBCLI()
    parser = argparse.ArgumentParser(description="ADB CLI Companion")
    
    subparsers = parser.add_subparsers(dest='cmd', help='Command')
    
    subparsers.add_parser('info', help='Device info')
    
    apps_p = subparsers.add_parser('apps', help='List apps')
    apps_p.add_argument('--filter', help='Filter apps by keyword')
    
    uninstall_p = subparsers.add_parser('uninstall', help='Uninstall app')
    uninstall_p.add_argument('pkg')
    
    revoke_p = subparsers.add_parser('revoke', help='Revoke permission')
    revoke_p.add_argument('pkg')
    revoke_p.add_argument('perm')
    
    screenshot_p = subparsers.add_parser('screenshot', help='Take screenshot')
    screenshot_p.add_argument('--path', default='/tmp/screen.png')
    
    reboot_p = subparsers.add_parser('reboot', help='Reboot device')
    reboot_p.add_argument('--mode', default='system', choices=['system', 'recovery', 'bootloader'])
    
    args = parser.parse_args()
    
    if args.cmd == 'info': cli.info()
    elif args.cmd == 'apps': cli.apps(args.filter if 'filter' in args else None)
    elif args.cmd == 'uninstall': cli.uninstall(args.pkg)
    elif args.cmd == 'revoke': cli.revoke(args.pkg, args.perm)
    elif args.cmd == 'screenshot': cli.screenshot(args.path if 'path' in args else '/tmp/screen.png')
    elif args.cmd == 'reboot': cli.reboot(args.mode if 'mode' in args else 'system')
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
