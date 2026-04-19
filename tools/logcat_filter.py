#!/usr/bin/env python3
"""
logcat_filter.py -- Advanced logcat filtering and monitoring
Usage: python3 logcat_filter.py --app com.example --level D|E|W
       python3 logcat_filter.py --filter "Exception|Error" --save crash.log
       python3 logcat_filter.py --app com.example --follow
"""
import subprocess, argparse, sys, re
from datetime import datetime

def stream_logcat(app_filter=None, level=None, pattern=None, follow=False, output_file=None):
    flags = "-v threadtime"
    cmd = f"adb logcat {flags}"
    
    out_file = open(output_file, "w") if output_file else None
    
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                              stderr=subprocess.DEVNULL, text=True)
        
        for line in proc.stdout:
            if not line.strip(): continue
            
            # Filter by app (PID from ps)
            if app_filter:
                if app_filter not in line:
                    continue
            
            # Filter by level
            if level:
                if not re.search(rf"\s{level}\s", line):
                    continue
            
            # Filter by pattern
            if pattern and not re.search(pattern, line, re.IGNORECASE):
                continue
            
            print(line.rstrip())
            if out_file:
                out_file.write(line)
                out_file.flush()
        
        if not follow:
            break
    
    except KeyboardInterrupt:
        pass
    finally:
        if out_file:
            out_file.close()
        proc.terminate()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", help="Filter by app/package keyword")
    parser.add_argument("--level", choices=["V","D","I","W","E","F"], help="Min log level")
    parser.add_argument("--filter", help="Regex pattern filter")
    parser.add_argument("--follow", action="store_true", help="Keep following (Ctrl+C to stop)")
    parser.add_argument("--save", help="Save to file")
    
    args = parser.parse_args()
    stream_logcat(args.app, args.level, args.filter, args.follow, args.save)

if __name__ == "__main__":
    main()
