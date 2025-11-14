/**
 * Electron Main Process
 * Automatically starts Flask server and opens browser window
 */

const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

let mainWindow;
let flaskProcess;
const FLASK_PORT = 5000;
const FLASK_URL = `http://127.0.0.1:${FLASK_PORT}`;

/**
 * Check if Flask server is running
 */
function checkFlaskServer() {
    return new Promise((resolve) => {
        const req = http.get(FLASK_URL, (res) => {
            resolve(res.statusCode === 200);
        });
        req.on('error', () => resolve(false));
        req.setTimeout(1000, () => {
            req.destroy();
            resolve(false);
        });
    });
}

/**
 * Wait for Flask server to start
 */
async function waitForFlask(maxAttempts = 30) {
    for (let i = 0; i < maxAttempts; i++) {
        const isRunning = await checkFlaskServer();
        if (isRunning) {
            console.log('✅ Flask server is ready!');
            return true;
        }
        console.log(`⏳ Waiting for Flask server... (${i + 1}/${maxAttempts})`);
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    return false;
}

/**
 * Start Flask server
 */
function startFlaskServer() {
    return new Promise((resolve, reject) => {
        console.log('🚀 Starting Flask server...');
        
        // Determine Python executable path
        const pythonPath = path.join(__dirname, 'bin', 'python');
        const scriptPath = path.join(__dirname, 'web_story_server_enhanced.py');
        
        // Start Flask process
        flaskProcess = spawn(pythonPath, [scriptPath], {
            cwd: __dirname,
            env: {
                ...process.env,
                FLASK_ENV: 'production',
                PYTHONUNBUFFERED: '1'
            }
        });
        
        // Log Flask output
        flaskProcess.stdout.on('data', (data) => {
            console.log(`[Flask] ${data.toString().trim()}`);
        });
        
        flaskProcess.stderr.on('data', (data) => {
            console.error(`[Flask Error] ${data.toString().trim()}`);
        });
        
        flaskProcess.on('error', (error) => {
            console.error('❌ Failed to start Flask:', error);
            reject(error);
        });
        
        flaskProcess.on('close', (code) => {
            console.log(`Flask process exited with code ${code}`);
        });
        
        // Give Flask a moment to start
        setTimeout(() => resolve(), 2000);
    });
}

/**
 * Create the main application window
 */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        title: 'AI Story Generator',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        },
        backgroundColor: '#1a1a1a',
        show: false // Don't show until ready
    });
    
    // Load Flask app
    mainWindow.loadURL(FLASK_URL);
    
    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        console.log('✅ Application window opened!');
    });
    
    // Handle window closed
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
    
    // Open DevTools in development (comment out for production)
    // mainWindow.webContents.openDevTools();
}

/**
 * Initialize application
 */
async function initialize() {
    try {
        // Start Flask server
        await startFlaskServer();
        
        // Wait for server to be ready
        const serverReady = await waitForFlask();
        
        if (!serverReady) {
            console.error('❌ Flask server failed to start in time');
            app.quit();
            return;
        }
        
        // Create window
        createWindow();
        
    } catch (error) {
        console.error('❌ Initialization failed:', error);
        app.quit();
    }
}

/**
 * App event handlers
 */
app.whenReady().then(initialize);

app.on('window-all-closed', () => {
    // Kill Flask server
    if (flaskProcess) {
        console.log('🛑 Stopping Flask server...');
        flaskProcess.kill();
    }
    
    // Quit app
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('will-quit', () => {
    // Ensure Flask is killed
    if (flaskProcess) {
        flaskProcess.kill();
    }
});

/**
 * Handle uncaught errors
 */
process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error);
});
