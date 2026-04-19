#!/usr/bin/env python3
"""
package_manager.py -- Full package management CLI
List, install, uninstall, enable/disable apps via ADB
Usage: python3 package_manager.py --list [--user|--system|--all]
       python3 package_manager.py --install app.apk
       python3 package_manager.py --uninstall com.example.app
       python3 package_manager.py --disable com.example.app
"""
import subprocess, argparse, sys

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def list_packages(filter_type="all"):
    flags = {
        "user": "-3",
        "system": "-s",
        "all": ""
    }
    out = adb(f"pm list packages {flags.get(filter_type, '')}")
    pkgs = sorted([l.split(":")[1] for l in out.splitlines() if l.startswith("package:")])
    return pkgs

def install(apk_path):
    result = adb(f"install -r {apk_path}")
    return "Success" in result

def uninstall(pkg, keep_data=False):
    flag = "-k" if keep_data else ""
    result = adb(f"uninstall {flag} {pkg}")
    return "Success" in result

def disable(pkg):
    adb(f"pm disable-user --user 0 {pkg}")
    return True

def enable(pkg):
    adb(f"pm enable {pkg}")
    return True

def get_size(pkg):
    out = adb(f"pm dump {pkg} | grep 'versionCode'")
    return out

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # List packages
    list_cmd = subparsers.add_parser("list", help="List packages")
    list_cmd.add_argument("--user", action="store_const", const="user", dest="type", default="all")
    list_cmd.add_argument("--system", action="store_const", const="system", dest="type")
    list_cmd.add_argument("--filter", help="Filter by name")

    # Install
    install_cmd = subparsers.add_parser("install")
    install_cmd.add_argument("apk", help="APK file path")

    # Uninstall
    uninstall_cmd = subparsers.add_parser("uninstall")
    uninstall_cmd.add_argument("package", help="Package name")
    uninstall_cmd.add_argument("--keep-data", action="store_true")

    # Enable/disable
    subparsers.add_parser("disable").add_argument("package")
    subparsers.add_parser("enable").add_argument("package")

    args = parser.parse_args()

    if args.command == "list":
        pkgs = list_packages(args.type)
        if args.filter:
            pkgs = [p for p in pkgs if args.filter.lower() in p.lower()]
        for pkg in pkgs:
            print(pkg)
        print(f"\nTotal: {len(pkgs)}")

    elif args.command == "install":
        ok = install(args.apk)
        print(f"{'✓ Installed' if ok else '✗ Failed'}: {args.apk}")

    elif args.command == "uninstall":
        ok = uninstall(args.package, args.keep_data)
        print(f"{'✓ Uninstalled' if ok else '✗ Failed'}: {args.package}")

    elif args.command == "disable":
        disable(args.package)
        print(f"✓ Disabled: {args.package}")

    elif args.command == "enable":
        enable(args.package)
        print(f"✓ Enabled: {args.package}")

if __name__ == "__main__":
    main()
