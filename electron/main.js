const { app, BrowserWindow } = require('electron')
const path = require('path')
const log = require('electron-log');
const Store = require("electron-store")
const storage = new Store();
require('dotenv').config()

const axios = require('axios').default;
const isDev = require('electron-is-dev')
const { spawn } = require("child_process")

const PY_PORT = 8001;
const UI_PORT = 3000;
const serverURL = `http://localhost:${PY_PORT}`
const uiURL = `http://localhost:${UI_PORT}`

if(isDev) {
  log.transports.file.resolvePath = () => path.join(__dirname, '/logsdev.log');
} else {
  log.transports.file.resolvePath = () => path.join(__dirname, '/logsmain.log');
}

log.transports.file.level = "info";
log.transports.console.format = '{text}'
log.transports.file.format = '{text}'

exports.log = (entry) => log.info(entry)

require('@electron/remote/main').initialize()

function _log(...args) {
  console.log(...args);
  log.info(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' '));
}

function _logError(...args) {
  console.error(...args);
  log.error(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' '));
}

// needs error handling?
function getWindowSettings () {
  const default_bounds = [800, 600]

  const size = storage.get('win-size');

  if (size) return size;
  else {
    storage.set("win-size", default_bounds);
    return default_bounds;
  }
}

function saveBounds (bounds) {
  storage.set("win-size", bounds)
}


function createWindow() {
  //get window size
  const bounds = getWindowSettings();
  _log('bounds:',bounds)

  // Create the browser window.
  const win = new BrowserWindow({
    width: bounds[0],
    height: bounds[1],
    webPreferences: {
      nodeIntegration: true,
      enableRemoteModule: true,
      webSecurity: false,
    }
  })
  if (isDev) {
    win.webContents.openDevTools()
  } 
  
  _log("storing user preferences in: ",app.getPath('userData'));
  
  // save size of window when resized
  win.on("resized", () => saveBounds(win.getSize()));
 
  win.loadURL(
    isDev
      ? uiURL
      : `file://${path.join(__dirname, './build/index.html')}`
  )
}

const installExtensions = () => {
  try{
    const installationProcess = spawn(
      path.join(__dirname, "./py_dist/main/main"),
      [
        "-i"
      ]
    );

    _log("installing idaes extensions");

    var scriptOutput = "";
    installationProcess.stdout.setEncoding('utf8');
    installationProcess.stdout.on('data', function(data) {
        log.info(data);
        data=data.toString();
        scriptOutput+=data;
    });

    installationProcess.stderr.setEncoding('utf8');
    installationProcess.stderr.on('data', function(data) {
        log.info(data);
        data=data.toString();
        scriptOutput+=data;
    });
    
    return installationProcess;
  } catch (error) {
    _logError("unable to spawn extensions process:", error);
    return null;
  }
}

const startServer = () => {
    if (isDev) {
      const backendProcess = spawn("uvicorn", 
        [
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            PY_PORT
        ],
        {
            cwd: '../backend/app'
        }
      );
      
      backendProcess.on('error', (error) => {
        _logError('Dev backend process failed to start:', error);
      });
      
      return backendProcess;
    } else {
      try {
        const backendProcess = spawn(
          path.join(__dirname, "./py_dist/main/main"),
          [
            "-p"
          ]
        );
        
        var scriptOutput = "";
        backendProcess.stdout.setEncoding('utf8');
        backendProcess.stdout.on('data', function(data) {
            _log('stdout:', data.toString());
            scriptOutput+=data;
        });

        backendProcess.stderr.setEncoding('utf8');
        backendProcess.stderr.on('data', function(data) {
            _log('stderr:', data.toString());
            scriptOutput+=data;
        });
        
        backendProcess.on('error', (error) => {
          _logError('Production backend process failed to start:', error);
        });
        
        _log("Python process started in built mode");
        return backendProcess;
      } catch (error) {
        _logError("unable to start python process in build mode:", error);
        return null;
      }
    }
}


app.whenReady().then(() => {
    _log(`isDev is ${isDev}`)
    // Entry point
    if (isDev) {
      createWindow()
    } else {
      let win = createWindow();
      _log("created window")
      let serverProcess
      _log("calling installationProcess = installExtensions()")
      let installationProcess = installExtensions()
      _log("finished call installExtensions()")
      
      const handleInstallationComplete = (code) => {
        if (code !== 0) {
          _logError(`Installation process exited with code ${code}`)
        }
        _log('starting server')
        serverProcess = startServer()

        if (!serverProcess) {
          _logError('Failed to start server process')
          app.quit()
          return
        }

        // Add error listener for server process
        serverProcess.on('error', (error) => {
          _logError('Server process error:', error)
          app.quit()
        })

        serverProcess.on('exit', (code) => {
          _logError(`Server process exited with code ${code}`)
          app.quit()
        })

        // Start Window 
        const startUp = (url, appName, spawnedProcess, successFn, maxTrials=15) => {
            let trialCount = 0
            const attemptConnection = () => {
                axios.get(url).then(() => {
                    _log(`${appName} is ready at ${url}!`)
                    if (successFn) successFn()
                })
                .catch(async () => {
                    _log(`Waiting to be able to connect ${appName} at ${url}... (attempt ${trialCount + 1}/${maxTrials})`)
                    trialCount += 1
                    if (trialCount < maxTrials) {
                        await new Promise(resolve => setTimeout(resolve, 2000))
                        attemptConnection()
                    }
                    else {
                        _logError(`Exceeded maximum trials to connect to ${appName}`)
                        spawnedProcess.kill('SIGINT')
                        app.quit()
                    }
                });
            };
            attemptConnection()
        };

        startUp(serverURL, 'FastAPI Server', serverProcess, createWindow)
      }

      // Add listeners for installation process
      if (!installationProcess) {
        _logError('Installation process failed to start')
        app.quit()
        return
      }

      installationProcess.on('error', (error) => {
        _logError('Installation process error:', error)
        app.quit()
      })

      installationProcess.on('exit', handleInstallationComplete)

      // Set aggressive timeout for installation process (30 seconds - should complete much faster)
      const installationTimeout = setTimeout(() => {
        if (installationProcess && !installationProcess.killed) {
          _logError('Installation process exceeded 30 second timeout, force-killing')
          try {
            installationProcess.kill('SIGKILL')  // Aggressive kill
          } catch (e) {
            _logError('Failed to kill installation process:', e)
          }
        }
      }, 30 * 1000)

      installationProcess.on('exit', () => {
        clearTimeout(installationTimeout)
      })
    }
    
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

// For windows & linux platforms
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
})


