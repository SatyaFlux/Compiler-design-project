import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const backendDir = path.join(__dirname, 'backend');
const frontendDir = path.join(__dirname, 'frontend');

const pythonExe = process.platform === 'win32'
  ? path.join(backendDir, '.venv', 'Scripts', 'python.exe')
  : path.join(backendDir, '.venv', 'bin', 'python');

const backend = spawn(pythonExe, ['app.py'], {
  cwd: backendDir,
  stdio: 'inherit',
});

const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const frontend = spawn(npmCmd, ['run', 'dev'], {
  cwd: frontendDir,
  stdio: 'inherit',
  shell: process.platform === 'win32',
});

function shutdown() {
  backend.kill();
  frontend.kill();
  process.exit(0);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

backend.on('exit', (code) => {
  if (code !== null && code !== 0) {
    console.error(`Backend exited with code ${code}`);
  }
});

frontend.on('exit', (code) => {
  if (code !== null && code !== 0) {
    console.error(`Frontend exited with code ${code}`);
  }
  backend.kill();
  process.exit(code ?? 0);
});
