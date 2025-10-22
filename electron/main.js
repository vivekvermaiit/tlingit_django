const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

let djangoProcess = null;
let mainWindow = null;

// configure these
const HOST = '127.0.0.1';
const PORT = 8000;
const URL = `http://${HOST}:${PORT}/corpus/entries/001`;
const START_TIMEOUT_MS = 20000; // max time to wait for server (20s)
const POLL_INTERVAL_MS = 300;   // how often to poll

function getDjangoBinaryPath() {
  // Electron __dirname will be tlingit_django/electron
  // PyInstaller binary is at ../tlingit_app/dist/tlingit_backend
  let binary = path.join(__dirname, '..', 'tlingit_app', 'dist', 'tlingit_backend');

  if (process.platform === 'win32') {
    binary += '.exe';
  }
  return binary;
}

function startDjango() {
  const binary = getDjangoBinaryPath();

  // spawn the binary with arguments similar to how you run it:
  // ./dist/tlingit_backend runserver --noreload 127.0.0.1:8000
  const args = ['runserver', '--noreload', `${HOST}:${PORT}`];

  // spawn without shell (safer)
  djangoProcess = spawn(binary, args, { stdio: ['ignore', 'pipe', 'pipe'] });

  djangoProcess.stdout.on('data', (data) => {
    console.log(`[django stdout] ${data.toString()}`);
  });

  djangoProcess.stderr.on('data', (data) => {
    console.error(`[django stderr] ${data.toString()}`);
  });

  djangoProcess.on('exit', (code, signal) => {
    console.log(`Django process exited (code=${code}, signal=${signal})`);
    // optionally close the app if backend exits unexpectedly:
    // app.quit();
  });

  return djangoProcess;
}

function waitForServer(url, timeoutMs) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    (function poll() {
      const req = http.get(url, (res) => {
        // if any 2xx or 3xx response -> consider server up
        if (res.statusCode >= 200 && res.statusCode < 400) {
          resolve();
        } else {
          // got a response but not good — maybe server ready but route missing,
          // still count this as "server is responding"
          resolve();
        }
        res.resume();
      });

      req.on('error', (err) => {
        if (Date.now() - start >= timeoutMs) {
          reject(new Error('Timeout waiting for Django server to start'));
        } else {
          setTimeout(poll, POLL_INTERVAL_MS);
        }
      });

      req.setTimeout(2000, () => {
        req.abort();
        if (Date.now() - start >= timeoutMs) {
          reject(new Error('Timeout waiting for Django server to start'));
        } else {
          setTimeout(poll, POLL_INTERVAL_MS);
        }
      });
    })();
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadURL(URL);
  // optional: show devtools
  // mainWindow.webContents.openDevTools();
}

app.on('ready', async () => {
  try {
    console.log('Starting Django backend...');
    startDjango();

    // wait until http://127.0.0.1:8000/ responds
    await waitForServer(URL, START_TIMEOUT_MS);
    console.log('Django server is up — launching Electron window.');
    createWindow();
  } catch (err) {
    console.error('Failed to start Django server:', err);
    dialog.showErrorBox('Startup error', `Could not start the backend: ${err.message}`);
    // Kill the process if it exists
    if (djangoProcess) {
      try { djangoProcess.kill(); } catch (e) {}
    }
    app.quit();
  }
});

app.on('window-all-closed', () => {
  // On macOS apps usually stay active until explicit quit, but we'll quit.
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (djangoProcess) {
    try {
      djangoProcess.kill();
    } catch (e) {
      console.error('Error killing django process:', e);
    }
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
