use clap::{Parser, Subcommand};
use std::process::Command;

#[derive(Parser)]
#[command(name = "adb-cli")]
#[command(about = "Fast ADB command wrapper")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// List all connected devices
    Devices,
    /// Get device info
    Info,
    /// Install APK
    Install { apk: String },
    /// Uninstall package
    Uninstall { package: String },
    /// Run shell command
    Shell { cmd: String },
    /// Debloat device (interactive)
    Debloat,
    /// Monitor FPS
    Fps,
}

fn run_adb(args: &[&str]) -> String {
    let output = Command::new("adb")
        .args(args)
        .output()
        .expect("Failed to execute adb");
    String::from_utf8_lossy(&output.stdout).to_string()
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Devices => {
            println!("{}", run_adb(&["devices"]));
        }
        Commands::Info => {
            println!("Model: {}", run_adb(&["shell", "getprop ro.product.model"]).trim());
            println!("Android: {}", run_adb(&["shell", "getprop ro.build.version.release"]).trim());
            println!("Storage: {}", run_adb(&["shell", "df -h /data"]).trim());
        }
        Commands::Install { apk } => {
            println!("Installing {}", apk);
            println!("{}", run_adb(&["install", "-r", &apk]));
        }
        Commands::Uninstall { package } => {
            println!("Uninstalling {}", package);
            println!("{}", run_adb(&["uninstall", &package]));
        }
        Commands::Shell { cmd } => {
            println!("{}", run_adb(&["shell", &cmd]));
        }
        Commands::Debloat => {
            println!("Interactive debloat mode");
            // Placeholder
            println!("Use: adb-cli shell 'pm list packages -3' to see user apps");
        }
        Commands::Fps => {
            println!("Monitoring FPS (Ctrl+C to stop)");
            println!("{}", run_adb(&["shell", "dumpsys gfxinfo | grep -A 5 'frames rendered'"]));
        }
    }
}
