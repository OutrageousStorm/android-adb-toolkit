/**
 * scheduler.ts - TypeScript ADB task scheduler
 * Run ADB commands on a schedule: time-based, event-based, or interval-based
 * Usage: npx ts-node scheduler.ts --config tasks.json
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';

const execPromise = promisify(exec);

interface Task {
  id: string;
  description: string;
  command: string;
  schedule: 'immediate' | 'daily' | 'hourly' | 'interval';
  time?: string; // HH:MM for daily
  intervalMs?: number; // for interval
  enabled: boolean;
}

interface Config {
  tasks: Task[];
  logFile?: string;
}

async function runAdb(cmd: string): Promise<string> {
  try {
    const { stdout, stderr } = await execPromise(`adb shell ${cmd}`);
    return stdout.trim();
  } catch (e: any) {
    throw new Error(\`ADB failed: \${e.message}\`);
  }
}

function log(msg: string) {
  const ts = new Date().toISOString();
  console.log(\`[\${ts}] \${msg}\`);
}

function scheduleDaily(task: Task, hour: number, minute: number) {
  const runTask = async () => {
    try {
      log(\`▶️  Running: \${task.id}\`);
      const result = await runAdb(task.command);
      log(\`✅ \${task.id}: \${result.substring(0, 50)}\`);
    } catch (e: any) {
      log(\`❌ \${task.id}: \${e.message}\`);
    }
  };

  const now = new Date();
  let next = new Date();
  next.setHours(hour, minute, 0, 0);

  if (next <= now) {
    next.setDate(next.getDate() + 1);
  }

  const delay = next.getTime() - now.getTime();
  setTimeout(() => {
    runTask();
    setInterval(runTask, 24 * 60 * 60 * 1000); // repeat daily
  }, delay);

  log(\`📅 \${task.id} scheduled for \${next.toLocaleTimeString()}\`);
}

function scheduleInterval(task: Task, intervalMs: number) {
  const runTask = async () => {
    try {
      const result = await runAdb(task.command);
      log(\`✅ \${task.id}: \${result.substring(0, 30)}\`);
    } catch (e: any) {
      log(\`❌ \${task.id}: \${e.message}\`);
    }
  };

  runTask(); // run immediately
  setInterval(runTask, intervalMs);
  log(\`⏱️  \${task.id} scheduled every \${intervalMs / 1000}s\`);
}

async function loadConfig(filePath: string): Promise<Config> {
  const data = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(data);
}

async function main() {
  const configPath = process.argv[3] || 'tasks.json';

  if (!fs.existsSync(configPath)) {
    console.log(\`Config not found: \${configPath}\`);
    console.log('Create tasks.json with:');
    console.log(JSON.stringify({
      tasks: [
        { id: 'morning_doze', description: 'Enable doze in morning',
          command: 'dumpsys deviceidle step deep', schedule: 'daily',
          time: '06:00', enabled: true }
      ]
    }, null, 2));
    return;
  }

  const config = await loadConfig(configPath);
  log(\`📋 Loaded \${config.tasks.length} tasks\`);

  for (const task of config.tasks) {
    if (!task.enabled) continue;

    if (task.schedule === 'immediate') {
      const result = await runAdb(task.command);
      log(\`✅ \${task.id}: \${result.substring(0, 50)}\`);
    } else if (task.schedule === 'daily' && task.time) {
      const [hour, minute] = task.time.split(':').map(Number);
      scheduleDaily(task, hour, minute);
    } else if (task.schedule === 'interval' && task.intervalMs) {
      scheduleInterval(task, task.intervalMs);
    }
  }

  log('🚀 Scheduler active');
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
