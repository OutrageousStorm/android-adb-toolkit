#!/usr/bin/env python3
"""
sensor_monitor.py -- Real-time Android sensor monitoring (accelerometer, gyro, mag, light, prox)
Usage: python3 sensor_monitor.py [--type accel|gyro|light] [--duration 60] [--csv output.csv]
"""
import subprocess, re, argparse, csv, time
from datetime import datetime

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

SENSORS = {
    "accel": "android.sensor.accelerometer",
    "gyro": "android.sensor.gyroscope",
    "mag": "android.sensor.magnetic_field",
    "light": "android.sensor.light",
    "prox": "android.sensor.proximity",
    "temp": "android.sensor.ambient_temperature",
    "pressure": "android.sensor.pressure",
}

def list_sensors():
    """List all available sensors on device"""
    out = adb("cmd sensorservice list")
    print("\n📊 Available Sensors")
    print("=" * 50)
    print(out)

def monitor_sensor(sensor_name, duration=None, csv_file=None):
    """Monitor a sensor in real time"""
    sensor_type = SENSORS.get(sensor_name, sensor_name)
    
    print(f"\n📈 Monitoring: {sensor_name}")
    if duration:
        print(f"Duration: {duration} seconds")
    print("Ctrl+C to stop\n")

    # dumpsys sensorservice | grep active (shows active sensors)
    # Use getevent to capture sensor events
    proc = subprocess.Popen(
        "adb shell getevent /dev/input/event*",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )

    rows = []
    start = time.time()
    line_num = 0

    try:
        for line in proc.stdout:
            if duration and (time.time() - start) > duration:
                break
            
            # Parse getevent output: /dev/input/eventX: type type_code value
            m = re.match(r'/dev/input/event\d+:\s+(\w+)\s+(\w+)\s+([\da-f]+)', line)
            if m:
                ev_type = m.group(1)
                code = m.group(2)
                val = int(m.group(3), 16)
                ts = datetime.now().isoformat()
                
                if line_num % 10 == 0:  # Print every 10 samples
                    print(f"[{ts}] {ev_type} {code} = {val}")
                
                rows.append((ts, ev_type, code, val))
                line_num += 1
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()

    print(f"\n✓ Collected {line_num} sensor events")
    
    if csv_file and rows:
        with open(csv_file, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['timestamp', 'type', 'code', 'value'])
            w.writerows(rows)
        print(f"✓ Exported to {csv_file}")

def main():
    parser = argparse.ArgumentParser(description="Real-time Android sensor monitor")
    parser.add_argument("--type", choices=list(SENSORS.keys()), default="accel", help="Sensor type")
    parser.add_argument("--duration", type=int, help="Monitor duration in seconds")
    parser.add_argument("--csv", help="Export to CSV file")
    parser.add_argument("--list", action="store_true", help="List available sensors")
    args = parser.parse_args()

    if args.list:
        list_sensors()
    else:
        monitor_sensor(args.type, args.duration, args.csv)

if __name__ == "__main__":
    main()
