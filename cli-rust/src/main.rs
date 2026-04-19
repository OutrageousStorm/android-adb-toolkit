// adb-cli-rs — Ultra-fast Rust ADB wrapper
// Compile: cargo build --release
// Usage: ./adb-cli-rs device-info
//        ./adb-cli-rs list-apps
//        ./adb-cli-rs screenshot output.png

use std::process::Command;
use std::env;

fn adb(cmd: &[&str]) -> String {
    let output = Command::new("adb")
        .args(cmd)
        .output()
        .expect("Failed to run adb");
    String::from_utf8_lossy(&output.stdout).to_string()
}

fn device_info() {
    println!("📱 Device Info\n");
    println!("Model:       {}", adb(&["shell", "getprop", "ro.product.model"]).trim());
    println!("Android:     {}", adb(&["shell", "getprop", "ro.build.version.release"]).trim());
    println!("CPU:         {}", adb(&["shell", "getprop", "ro.product.cpu.abi"]).trim());
    println!("RAM (Total): {}", adb(&["shell", "cat", "/proc/meminfo"]).lines().next().unwrap_or("N/A"));
    println!("Storage:     {}", adb(&["shell", "df", "-h", "/data"]).lines().last().unwrap_or("N/A"));
    println!("Battery:     {}", adb(&["shell", "dumpsys", "battery"]).lines()
        .find(|l| l.contains("level:")).unwrap_or("N/A"));
}

fn list_apps(user_only: bool) {
    let flag = if user_only { "-3" } else { "" };
    let output = adb(&["shell", "pm", "list", "packages", flag]);
    println!("📦 Installed Apps ({})\n", if user_only { "user" } else { "all" });
    for line in output.lines() {
        if let Some(pkg) = line.strip_prefix("package:") {
            println!("{}", pkg);
        }
    }
}

fn screenshot(output: &str) {
    adb(&["exec-out", "screencap", "-p"]);
    println!("✅ Screenshot saved to {}", output);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <command> [args]", args[0]);
        eprintln!("Commands:");
        eprintln!("  device-info           Show device properties");
        eprintln!("  list-apps [--user]    List installed packages");
        eprintln!("  screenshot <file>     Capture screen");
        return;
    }

    match args[1].as_str() {
        "device-info" => device_info(),
        "list-apps" => list_apps(args.len() > 2 && args[2] == "--user"),
        "screenshot" => {
            if args.len() < 3 {
                eprintln!("Usage: screenshot <output.png>");
                return;
            }
            screenshot(&args[2]);
        }
        _ => eprintln!("Unknown command: {}", args[1]),
    }
}
