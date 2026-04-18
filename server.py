#!/usr/bin/env python3
"""
server.py -- Lightweight ADB HTTP API server for scripting
Expose ADB commands as REST endpoints. Start server, make API calls from anywhere.
Usage: python3 server.py --port 8080
Then: curl http://localhost:8080/api/device/info
      curl -X POST http://localhost:8080/api/shell -d "cmd=pm list packages"
"""
import subprocess, json, argparse, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

def adb(cmd, serial=None):
    pre = f"adb -s {serial}" if serial else "adb"
    r = subprocess.run(f"{pre} shell {cmd}", shell=True, capture_output=True, text=True)
    return {"stdout": r.stdout.strip(), "stderr": r.stderr.strip(), "code": r.returncode}

def adb_raw(cmd, serial=None):
    pre = f"adb -s {serial}" if serial else "adb"
    r = subprocess.run(f"{pre} {cmd}", shell=True, capture_output=True, text=True)
    return {"stdout": r.stdout.strip(), "stderr": r.stderr.strip(), "code": r.returncode}

class ADBHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)

        if path == "/api/devices":
            result = adb_raw("devices")
            devices = [l.split()[0] for l in result["stdout"].splitlines()[1:] if l.strip()]
            self.send_json({"devices": devices})

        elif path == "/api/device/info":
            serial = query.get("serial", [None])[0]
            info = {
                "model": adb("getprop ro.product.model", serial)["stdout"],
                "android": adb("getprop ro.build.version.release", serial)["stdout"],
                "sdk": adb("getprop ro.build.version.sdk", serial)["stdout"],
                "battery": adb("dumpsys battery | grep level", serial)["stdout"],
            }
            self.send_json(info)

        elif path == "/api/packages":
            serial = query.get("serial", [None])[0]
            result = adb("pm list packages", serial)
            packages = [l.split(":")[1] for l in result["stdout"].splitlines() if l.startswith("package:")]
            self.send_json({"count": len(packages), "packages": packages[:50]})

        else:
            self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode()
        params = parse_qs(body)

        if path == "/api/shell":
            cmd = params.get("cmd", [""])[0]
            serial = params.get("serial", [None])[0]
            if not cmd:
                self.send_error(400)
                return
            result = adb(cmd, serial)
            self.send_json(result)

        elif path == "/api/install":
            # Expect: apk_path (on device or PC)
            apk = params.get("apk", [""])[0]
            serial = params.get("serial", [None])[0]
            result = adb_raw(f"install {apk}", serial)
            self.send_json(result)

        else:
            self.send_error(404)

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), ADBHandler)
    print(f"🚀 ADB HTTP Server running on {args.host}:{args.port}")
    print(f"Try: curl http://localhost:{args.port}/api/devices")
    print(f"     curl http://localhost:{args.port}/api/device/info?serial=device_serial")
    print(f"     curl -X POST http://localhost:{args.port}/api/shell -d 'cmd=getprop ro.product.model'")
    print("\nPress Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
