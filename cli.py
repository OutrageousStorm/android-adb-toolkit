#!/usr/bin/env python3
"""
cli.py -- Command-line interface for ADB toolkit
Easier than remembering adb commands. Autocomplete & history.
Usage: python3 cli.py
"""
import subprocess, sys, readline, argparse
from pathlib import Path

class ADBCli:
    def __init__(self):
        self.history_file = Path.home() / ".adb_cli_history"
        self.load_history()

    def load_history(self):
        if self.history_file.exists():
            with open(self.history_file) as f:
                for line in f:
                    readline.add_history(line.strip())

    def save_history(self):
        with open(self.history_file, "a") as f:
            f.write(readline.get_history_item(readline.get_current_history_length()) + "\n")

    def adb(self, cmd):
        r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
        return r.stdout.strip() or r.stderr.strip() or "OK"

    def cmd_getinfo(self, args):
        """Get device info"""
        props = [
            ("Model", "getprop ro.product.model"),
            ("Android", "getprop ro.build.version.release"),
            ("RAM", "cat /proc/meminfo | grep MemTotal"),
            ("Storage", "df -h /data | tail -1"),
        ]
        for label, cmd in props:
            val = self.adb(cmd)
            print(f"  {label:<15} {val}")

    def cmd_perms(self, args):
        """Revoke permissions interactively"""
        pkg = args.pkg if hasattr(args, 'pkg') else input("Package name: ").strip()
        if not pkg: return
        perms = [
            "ACCESS_FINE_LOCATION",
            "READ_CONTACTS",
            "RECORD_AUDIO",
            "READ_SMS",
            "CAMERA",
        ]
        print(f"\nPermissions to revoke from {pkg}:")
        for p in perms:
            revoke = input(f"  {p}? (y/N): ").strip().lower() == 'y'
            if revoke:
                self.adb(f"pm revoke {pkg} android.permission.{p}")
                print(f"    ✓ Revoked")

    def cmd_apps(self, args):
        """List user apps"""
        out = self.adb("pm list packages -3")
        apps = [l.split(":")[1] for l in out.splitlines() if l.startswith("package:")]
        print(f"\nFound {len(apps)} user apps:")
        for app in sorted(apps)[:20]:
            print(f"  {app}")
        if len(apps) > 20:
            print(f"  ... and {len(apps)-20} more")

    def cmd_screenshot(self, args):
        """Take screenshot"""
        filename = args.file if hasattr(args, 'file') else f"screenshot_{__import__('time').strftime('%Y%m%d_%H%M%S')}.png"
        subprocess.run(f"adb exec-out screencap -p > {filename}", shell=True)
        print(f"✓ Saved: {filename}")

    def interactive(self):
        """Interactive shell"""
        print("\n🔧 ADB CLI — type 'help' for commands\n")
        while True:
            try:
                cmd = input("adb> ").strip()
                if not cmd: continue
                if cmd == "help":
                    print("  getinfo    - device info")
                    print("  perms PKG  - revoke permissions")
                    print("  apps       - list apps")
                    print("  screenshot - take screenshot")
                    print("  shell CMD  - run adb shell command")
                    print("  quit       - exit")
                elif cmd == "quit": break
                elif cmd.startswith("getinfo"): self.cmd_getinfo(None)
                elif cmd.startswith("perms"): self.cmd_perms(type('args', (), {'pkg': cmd.split()[1] if len(cmd.split()) > 1 else None})())
                elif cmd.startswith("apps"): self.cmd_apps(None)
                elif cmd.startswith("screenshot"): self.cmd_screenshot(type('args', (), {'file': None})())
                elif cmd.startswith("shell "):
                    result = self.adb(cmd[6:])
                    print(result)
                else:
                    print(f"Unknown command: {cmd}")
                self.save_history()
            except KeyboardInterrupt:
                print("\nExiting...")
                break

def main():
    cli = ADBCli()
    cli.interactive()

if __name__ == "__main__":
    main()
