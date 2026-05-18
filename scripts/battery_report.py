#!/usr/bin/env python3
"""battery_report.py -- HTML battery consumption report"""
import subprocess, re
from datetime import datetime

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_battery_info():
    out = adb("dumpsys battery")
    info = {}
    for line in out.splitlines():
        if "level:" in line:
            info['level'] = int(re.search(r'\d+', line).group(0) or 0)
        if "temperature:" in line:
            info['temp'] = int(re.search(r'\d+', line).group(0) or 0)
        if "voltage:" in line:
            info['voltage'] = int(re.search(r'\d+', line).group(0) or 0)
        if "health:" in line:
            info['health'] = line.split(":")[-1].strip()
    return info

def main():
    print("📊 Generating battery report...")
    info = get_battery_info()
    
    html = f'''<!DOCTYPE html>
<html>
<head><title>Battery Report</title>
<style>body{{font-family:Arial;margin:20px}}
.card{{background:white;padding:20px;margin:10px 0;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
.battery-bar{{height:40px;background:#ddd;border-radius:4px;overflow:hidden}}
.fill{{height:100%;background:#4caf50;width:{info.get("level", 50)}%}}
</style></head>
<body><h1>🔋 Battery Report</h1>
<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<div class="card"><h2>Current Status</h2>
<div class="battery-bar"><div class="fill"></div></div>
<p><b>Level:</b> {info.get("level", "?")}%</p>
<p><b>Temp:</b> {info.get("temp", "?")}°C</p>
<p><b>Voltage:</b> {info.get("voltage", "?")}mV</p>
<p><b>Health:</b> {info.get("health", "?")}</p></div></body></html>'''
    
    with open("battery_report.html", "w") as f:
        f.write(html)
    
    print("✅ Saved to battery_report.html")
    print(f"   Level: {info.get('level')}% | Temp: {info.get('temp')}°C")

if __name__ == "__main__":
    main()
