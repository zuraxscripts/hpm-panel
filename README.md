# [HappinessMP](https://happinessmp.net/) Panel - Windows Edition

Web-based management panel for [HappinessMP](https://happinessmp.net/) servers on **Windows**.

This is a Windows-adapted fork of the original HPM Panel (originally Linux-only). It provides a browser UI for starting and stopping the server, live console access, file management, player management, resource and addon control, scheduled restarts, update checks, multi-user access, and Discord integration.

## Features

- Web control panel for [HappinessMP](https://happinessmp.net/)
- Start, stop, and restart server actions
- Live console with command input
- File manager with upload, download, edit, rename, delete, compress, and extract actions
- `settings.xml` management from the panel
- Resource and addon management
- Player list, player profiles, warnings, kick, ban, and direct messages
- User accounts with roles and permissions
- Admin action logs
- Built-in update checker for the panel and [HappinessMP](https://happinessmp.net/) server files
- Optional Discord bot and status embed integration
- Automatic first-run setup wizard
- Automatic download of the Windows [HappinessMP](https://happinessmp.net/) server package during setup
- Automatic installation of `hpm-connector` during setup

## Requirements

- **Windows 10/11** or **Windows Server 2019+**
- **Python 3.9+** (3.11 recommended) — [Download Python](https://www.python.org/downloads/)
- A **MySQL** or **MariaDB** database (or use XAMPP/WampServer for local DB)
- Internet access during initial setup

## Quick Installation (Easy Mode)

### 1. Install Python

Download and install Python from https://www.python.org/downloads/

**IMPORTANT:** During installation, check **"Add Python to PATH"** at the bottom of the installer.

### 2. Install a Database

You need a MySQL or MariaDB server. Options:
- **XAMPP** (easiest): https://www.apachefriends.org/ — includes MariaDB + phpMyAdmin
- **WampServer**: https://www.wampserver.com/
- **MySQL Installer**: https://dev.mysql.com/downloads/installer/

Create a database (e.g. `happinessmp`) and a user with full privileges to that database.

### 3. Install the Panel

1. Extract the panel files to any folder (e.g. `C:\HMP-Panel`)
2. Double-click **`install.bat`**
3. Wait for the installation to finish (it creates a virtual environment and installs dependencies)

### 4. Start the Panel

Double-click **`start.bat`**

Or for background/running without a console window:
- Double-click **`start_hidden.vbs`** (runs silently in the background)

### 5. Complete Setup

Open your browser and go to:

```
http://localhost:20000
```

The console will show a **4-digit Setup PIN**. Enter it in the browser and follow the wizard:

1. Enter the setup PIN
2. Create the admin account
3. Enter MariaDB/MySQL connection details
4. Wait for the panel to download and prepare the Windows server files

## Manual Installation

```batch
:: 1. Create virtual environment
python -m venv .venv

:: 2. Activate it  
.venv\Scripts\activate

:: 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

:: 4. Start the panel
python main.py --port 20000
```

## Files and Scripts

| File | Purpose |
|------|---------|
| `install.bat` | One-click installer (creates venv, installs deps) |
| `start.bat` | Start the panel in a console window |
| `start_hidden.vbs` | Start the panel silently in the background |
| `stop_panel.bat` | Stop any running panel processes |
| `main.py` | Launcher / entry point |
| `server_manager.py` | Main web panel server |
| `panel_config.json` | Panel configuration (created on first run) |

## Default Paths

- Panel port: `20000`
- Game server directory: `./HPNMP/`
- Game server executable: `./HPNMP/HappMP.exe`
- Logs directory: `./data/logs/`

## Changing the Port

**Option 1:** Pass it when starting:
```batch
start.bat --port 8080
```

**Option 2:** Set environment variable before starting:
```batch
set PANEL_PORT=8080
start.bat
```

**Option 3:** Edit `panel_config.json` after first run and change `panel_port`.

## Discord Bot Integration

Configure in the web panel under Settings > Discord Integration.

## Security Notes

- Use a strong admin password
- Do not expose the panel publicly without proper firewall rules
- Use HTTPS when exposing the panel to the internet (use a reverse proxy like Nginx or Caddy)
- Only give necessary permissions to non-admin users

## Troubleshooting

### "Python is not recognized"

Reinstall Python and make sure **"Add Python to PATH"** is checked.

### Panel does not start

Check that:
- No other application is using port 20000
- You ran `install.bat` first
- Windows Firewall is not blocking Python

### Cannot connect to database during setup

Make sure:
- MySQL/MariaDB is running (check XAMMP/WampServer control panel)
- The database exists and the user has privileges
- The host is correct (use `127.0.0.1` for local DB)

### "Module not found" errors

Run `install.bat` again to reinstall dependencies.

## Notes

- This Windows edition downloads the **Windows** version of HappinessMP server files automatically
- The server binary is named `HappMP.exe` (not `HappMP` as on Linux)
- The hpm-connector is installed as `hpm-connector.dll` (not `.so` as on Linux)
- For production use, consider running the panel as a Windows service using NSSM or Task Scheduler
