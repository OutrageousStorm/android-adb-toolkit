#!/usr/bin/env python3
"""
server.py -- Lightweight HTTP server for ADB commands
Exposes ADB as REST API for web UI and external tools.
Usage: python3 server.py --port 8000
"""
import subprocess, json, sys, argparse, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

class ADBHandler(BaseHTTPRequestHandler):
    def adb(self, cmd):
        r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
        return r.stdout.strip()

    def api_response(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)

        # /api/devices
        if path == "/api/devices":
            r = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
            devices = [l.split()[0] for l in r.stdout.splitlines()[1:] if "device" in l]
            return self.api_response({"devices": devices})

        # /api/getprop?key=ro.build.version.release
        if path == "/api/getprop":
            key = query.get("key", [""])[0]
            val = self.adb(f"getprop {key}")
            return self.api_response({"key": key, "value": val})

        # /api/packages
        if path == "/api/packages":
            filter_type = query.get("filter", ["all"])[0]  # all, user, system
            flag = {"user": "-3", "system": "-s"}.get(filter_type, "")
            pkgs = self.adb(f"pm list packages {flag}")
            pkg_list = [l.split(":")[1] for l in pkgs.splitlines() if "package:" in l]
            return self.api_response({"count": len(pkg_list), "packages": pkg_list[:100]})

        # /api/battery
        if path == "/api/battery":
            battery = self.adb("dumpsys battery | grep -E 'level|status|temperature'")
            return self.api_response({"battery_info": battery})

        # /api/storage
        if path == "/api/storage":
            internal = self.adb("df -h /data | tail -1")
            return self.api_response({"storage": internal})

        self.api_response({"error": "Unknown endpoint"}, 404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode()
        data = json.loads(body) if body else {}

        path = urlparse(self.path).path

        # /api/uninstall — POST {"package": "com.foo"}
        if path == "/api/uninstall":
            pkg = data.get("package", "")
            result = self.adb(f"pm uninstall -k --user 0 {pkg}")
            ok = "Success" in result
            return self.api_response({"success": ok, "package": pkg, "result": result})

        # /api/revoke — POST {"package": "com.foo", "permission": "android.permission.CAMERA"}
        if path == "/api/revoke":
            pkg = data.get("package", "")
            perm = data.get("permission", "")
            self.adb(f"pm revoke {pkg} {perm}")
            return self.api_response({"success": True, "package": pkg, "permission": perm})

        # /api/exec — POST {"command": "settings get system screen_brightness"}
        if path == "/api/exec":
            cmd = data.get("command", "")
            result = self.adb(cmd)
            return self.api_response({"command": cmd, "result": result})

        self.api_response({"error": "Unknown endpoint"}, 404)

    def log_message(self, format, *args):
        pass  # silence access logs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), ADBHandler)
    print(f"\n🚀 ADB API Server running on http://localhost:{args.port}")
    print(f"Endpoints:")
    print(f"  GET  /api/devices")
    print(f"  GET  /api/packages?filter=user|system")
    print(f"  GET  /api/battery")
    print(f"  GET  /api/storage")
    print(f"  POST /api/uninstall {{\"package\": \"...\"}}")
    print(f"  POST /api/exec {{\"command\": \"...\"}}")
    print(f"\nPress Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
