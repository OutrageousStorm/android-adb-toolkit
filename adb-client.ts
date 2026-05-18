// adb-client.ts -- Typed ADB client for programmatic device control
// Usage: import { ADBClient } from './adb-client.ts'
// Requires: Deno or Node.js with TypeScript

interface DeviceInfo {
    serial: string;
    state: 'device' | 'offline' | 'recovery' | 'bootloader';
    model: string;
    android: string;
    build: string;
}

interface AppInfo {
    package: string;
    label: string;
    versionCode: number;
    versionName: string;
}

export class ADBClient {
    private deviceSerial: string | null = null;

    async listDevices(): Promise<DeviceInfo[]> {
        const cmd = new Deno.Command('adb', {
            args: ['devices', '-l'],
        });
        const { stdout } = await cmd.output();
        const text = new TextDecoder().decode(stdout);
        
        return text
            .split('\n')
            .slice(1)
            .filter(line => line.trim())
            .map(line => {
                const parts = line.split(/\s+/);
                return {
                    serial: parts[0],
                    state: (parts[1] as any) || 'unknown',
                    model: parts.find(p => p.startsWith('model:'))?.replace('model:', '') || '',
                    android: parts.find(p => p.startsWith('device:'))?.replace('device:', '') || '',
                    build: parts.find(p => p.startsWith('transport_id:'))?.replace('transport_id:', '') || '',
                } as DeviceInfo;
            });
    }

    async connectDevice(serial: string): Promise<boolean> {
        this.deviceSerial = serial;
        const cmd = new Deno.Command('adb', {
            args: ['-s', serial, 'shell', 'getprop', 'ro.product.model'],
        });
        const { stdout } = await cmd.output();
        return new TextDecoder().decode(stdout).trim().length > 0;
    }

    async shell(cmd: string): Promise<string> {
        if (!this.deviceSerial) throw new Error('No device connected');
        const command = new Deno.Command('adb', {
            args: ['-s', this.deviceSerial, 'shell', cmd],
        });
        const { stdout } = await command.output();
        return new TextDecoder().decode(stdout).trim();
    }

    async getDeviceInfo(): Promise<Record<string, string>> {
        const props = [
            'ro.product.model',
            'ro.build.version.release',
            'ro.build.fingerprint',
            'ro.build.version.security_patch',
            'ro.boot.serialno',
        ];
        
        const info: Record<string, string> = {};
        for (const prop of props) {
            info[prop] = await this.shell(`getprop ${prop}`);
        }
        return info;
    }

    async getInstalledApps(): Promise<AppInfo[]> {
        const output = await this.shell('pm list packages -3 -U');
        const packages = output.split('\n').map(l => l.replace('package:', ''));
        
        const apps: AppInfo[] = [];
        for (const pkg of packages) {
            try {
                const dumpsys = await this.shell(`dumpsys package ${pkg}`);
                const label = dumpsys.match(/versionName=([^\s]+)/)?.[1] || pkg;
                apps.push({
                    package: pkg,
                    label: label,
                    versionCode: parseInt(dumpsys.match(/versionCode=(\d+)/)?.[1] || '0'),
                    versionName: label,
                });
            } catch (e) {
                // Skip on error
            }
        }
        return apps;
    }

    async installAPK(apkPath: string): Promise<boolean> {
        if (!this.deviceSerial) throw new Error('No device connected');
        const cmd = new Deno.Command('adb', {
            args: ['-s', this.deviceSerial, 'install', '-r', apkPath],
        });
        const { stdout } = await cmd.output();
        return new TextDecoder().decode(stdout).includes('Success');
    }

    async pushFile(src: string, dest: string): Promise<boolean> {
        if (!this.deviceSerial) throw new Error('No device connected');
        const cmd = new Deno.Command('adb', {
            args: ['-s', this.deviceSerial, 'push', src, dest],
        });
        const { stdout } = await cmd.output();
        return new TextDecoder().decode(stdout).includes('transferred');
    }
}

// Example usage:
// const client = new ADBClient();
// const devices = await client.listDevices();
// await client.connectDevice(devices[0].serial);
// const info = await client.getDeviceInfo();
// console.log(info);
