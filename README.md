<div align="center">
  <img src="templates/logo.png" alt="HappinessMP logo" width="160" />

  <h1>HMP Panel for Windows</h1>

  <p><strong>Web control panel for HappinessMP servers on Windows.</strong></p>

  <p>
    Start the server, watch the console, edit files, manage players, schedule restarts,
    sync the hpm-connector bridge, and keep panel/HappinessMP updates in one browser UI.
  </p>

  <p>
    <img alt="Windows target" src="https://img.shields.io/badge/Target-Windows%2010%2F11%20%7C%20Server-0078D6?style=for-the-badge&logo=windows&logoColor=white">
    <img alt="Python 3.9+" src="https://img.shields.io/badge/Python-3.9%2B-2563eb?style=for-the-badge&logo=python&logoColor=white">
    <img alt="MySQL/MariaDB" src="https://img.shields.io/badge/Database-MySQL%2FMariaDB-16a34a?style=for-the-badge">
    <img alt="One-click installer" src="https://img.shields.io/badge/Install-one--click%20.bat-f59e0b?style=for-the-badge">
  </p>

  <p>
    <a href="#what-it-does">What It Does</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#quick-start">Quick Start</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#first-run">First Run</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#files-and-scripts">Files &amp; Scripts</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#configuration">Configuration</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#linux-version">Linux Version</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#troubleshooting">Troubleshooting</a>
  </p>
</div>

---

> [!IMPORTANT]
> This is the **Windows edition** of HMP Panel. It runs on Windows 10/11 and Windows Server 2019+. For Linux, see the <a href="#linux-version">Linux Version</a> section.

> [!NOTE]
> HMP Panel for Windows requires MySQL or MariaDB for data storage (XAMPP, WampServer, or a standalone DB server).

## What It Does

HMP Panel is a browser-based operations panel for a HappinessMP server. It combines process control, live console access, file management, player moderation, restart scheduling, Discord integration, and an in-game connector bridge.

<table>
  <tr>
    <td width="33%" valign="top">
      <strong>Run the Server</strong><br />
      Start, stop, restart, auto-start, track uptime, see live CPU/RAM stats, and schedule daily or quick restarts.
    </td>
    <td width="33%" valign="top">
      <strong>Operate Faster</strong><br />
      Use the live console, send commands, edit <code>settings.xml</code>, manage resources/addons, upload/download files, zip/unzip.
    </td>
    <td width="33%" valign="top">
      <strong>Moderate Players</strong><br />
      Track profiles, warnings, notes, bans, kicks, direct messages, broadcast notices, and player identifiers.
    </td>
  </tr>
</table>

## Feature Matrix

| Area | Included |
| --- | --- |
| Server lifecycle | Start, stop, restart, auto-start, process detection, uptime, CPU/RAM samples |
| Console | Live output, history, command input, command logging |
| Setup | PIN-protected first run, admin account creation, HappinessMP Windows server download, hpm-connector installation |
| Storage | MySQL/MariaDB with encrypted credentials, optional JSON fallback files |
| HappinessMP config | Visual management for `settings.xml` fields |
| Files | Browse, read, edit, upload, download, rename, delete, zip, unzip, create folders |
| Resources | Start, stop, restart resources and addons from the panel |
| Players | Online list, saved profiles, identifiers, playtime, notes, warnings, kick, ban |
| In-game bridge | hpm-connector: heartbeat, player sync, pending moderation actions, panel secret auth |
| Users | Admin/user roles, per-user permissions, forced password change, display names, avatars |
| Logs | Per-user action logs and console action tracking |
| Discord | Optional bot token, warning channel, customizable status embed JSON with buttons/colors |
| Updates | Panel update checks from GitHub and HappinessMP server archive updates |

## Requirements

| Requirement | Notes |
| --- | --- |
| OS | Windows 10/11 or Windows Server 2019+ |
| Python | `3.9+` (3.11+ recommended) — [Download Python](https://www.python.org/downloads/) |
| Database | MySQL or MariaDB (XAMPP, WampServer, or standalone) |
| Network | Needed during first setup to download the HappinessMP Windows server archive |
| Internet | Required for update checks and hpm-connector downloads |

> **Important:** When installing Python, check **"Add Python to PATH"** at the bottom of the installer.

## Quick Start

### 1. Install a Database

You need MySQL or MariaDB. The easiest option is **XAMPP**:

1. Download from [apachefriends.org](https://www.apachefriends.org/)
2. Install and start Apache + MySQL from the XAMPP Control Panel
3. Open phpMyAdmin at `http://localhost/phpmyadmin`
4. Create a database (e.g. `happinessmp`) and a user with full privileges

### 2. Install the Panel

1. Extract the panel files to any folder (e.g. `C:\HMP-Panel`)
2. **Double-click `install.bat`** — it will:
   - Check your Python installation
   - Create a virtual environment (`.venv`)
   - Install all Python dependencies
   - Create start scripts

### 3. Start the Panel

**Option A — Console window (recommended for first run):**
Double-click **`start.bat`**

**Option B — Background (no visible window):**
Double-click **`start_hidden.vbs`**

**Option C — Custom port:**
Open a terminal in the panel folder and run:
```batch
start.bat --port 20000
```

### 4. Open the Panel

```text
http://localhost:20000
```

## First Run

The first launch is protected by a setup PIN visible in the console (or in `start.bat` window).

Setup asks for:

1. Setup PIN from the terminal
2. Admin username and password
3. Database connection details (host, port, user, password, database)

Setup then performs:

| Step | Result |
| --- | --- |
| Database | Saves encrypted DB credentials and creates required tables |
| Secret | Generates the panel secret if still using the default |
| Server files | Downloads the official HappinessMP Windows archive when missing |
| hpm-connector | Downloads and installs the latest connector release |
| Config | Updates connector config with the panel secret and host |
| User | Creates the first admin account |

Default paths:

| Item | Value |
| --- | --- |
| Panel port | `20000` |
| Server executable | `.\HPNMP\HappMP.exe` |
| Server directory | `.\HPNMP\` |
| Panel config | `.\panel_config.json` |
| Runtime data | `.\data\` |
| Logs | `.\data\logs\` |

## Files and Scripts

| File | Purpose |
| --- | --- |
| `install.bat` | **One-click installer** — creates venv, installs dependencies |
| `start.bat` | Starts the panel in a console window |
| `start_hidden.vbs` | Starts the panel silently in the background (no window) |
| `stop_panel.bat` | Stops any running panel Python processes |
| `main.py` | Launcher — installs deps, spawns server manager, handles restart |
| `server_manager.py` | Flask/Socket.IO panel — all routes, setup, server control |
| `storage.py` | Storage layer (MySQL + JSON fallback) |
| `db.py` | Database connection, encrypted credentials, schema |
| `updater.py` | Panel and HappinessMP updater worker |
| `requirements.txt` | Python dependencies |
| `panel_version.json` | Current panel version |
| `update_config.json` | Default update sources |
| `happiness_update.json` | HappinessMP Windows update metadata |
| `templates/` | Panel pages and UI assets |
| `locales/` | English and Czech translations |

## Configuration

### Port

**Option 1 — CLI argument:**
```batch
start.bat --port 8080
```

**Option 2 — Environment variable:**
```batch
set PANEL_PORT=8080
start.bat
```

**Option 3 — Config file:**
Edit `panel_config.json` after first run and change `panel_port`.

### Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `PANEL_PORT` / `PORT` | `20000` | Panel HTTP port |
| `PANEL_PRODUCTION` | `true` | Enables production defaults |
| `PANEL_ACCESS_LOGS` | `false` in production | Controls HTTP access logging |
| `PANEL_FORCE_HTTPS` | `false` | Redirects HTTP to HTTPS when enabled |
| `PANEL_SESSION_COOKIE_SECURE` | follows HTTPS flag | Marks session cookie secure |
| `HAPPINESS_DB_HOST` | `127.0.0.1` | Database server host |
| `HAPPINESS_DB_PORT` | `3306` | Database server port |
| `HAPPINESS_DB_USER` | `happinessmp` | Database user |
| `HAPPINESS_DB_PASSWORD` | — | Database password |
| `HAPPINESS_DB_NAME` | `happinessmp` | Database name |
| `HPM_UPDATE_CONFIG_URL` | empty | Optional remote update config JSON |
| `HPM_PANEL_REPO` | `zuraxscripts/hmp-panel` | GitHub repo for panel update checks |
| `HPM_HAPPINESS_UPDATE_URL` | default | HappinessMP update metadata URL override |
| `HPM_UPDATE_INTERVAL_MINUTES` | `10` | Background update check interval |

## Background Service (Windows)

### Option A — Task Scheduler (recommended)

1. Open **Task Scheduler**
2. Create a new task:
   - **Trigger:** At system startup
   - **Action:** Start a program
   - **Program:** `wscript.exe`
   - **Arguments:** `"C:\HMP-Panel\start_hidden.vbs"`
3. Save and enable the task

### Option B — NSSM (Non-Sucking Service Manager)

1. Download NSSM from [nssm.cc](https://nssm.cc/)
2. Install as a service:
   ```batch
   nssm install HMPPanel "C:\HMP-Panel\.venv\Scripts\python.exe" "C:\HMP-Panel\main.py" --port 20000
   nssm start HMPPanel
   ```

## Discord Bot Integration

Configure in the web panel under **Settings > Discord Integration**:

| Field | Purpose |
| --- | --- |
| Token | Discord bot token |
| Guild ID | Discord server (guild) ID |
| Warnings Channel | Channel for player warning notifications |
| Status Embed | Customizable embed for server status display |

## In-Game Bridge

During setup, HMP Panel installs the hpm-connector bridge:

| Component | Location | Purpose |
| --- | --- | --- |
| hpm-connector | `HPNMP\resources\hpm-connector\` | Sends player sync, heartbeat, and receives pending actions |
| Connector binary | `hpm-connector.dll` (Windows) | Compiled connector module |
| Resource config | `HPNMP\settings.xml` | Updated to load the connector resource |

## Updating

HMP Panel can check and apply updates for:

| Target | Source |
| --- | --- |
| Panel | GitHub repository from `update_config.json` or `HPM_PANEL_REPO` |
| HappinessMP server | Archive URL from `happiness_update.json` or `HPM_HAPPINESS_UPDATE_URL` |

The updater stores state in `data\update_status.json`, `data\update_job.json`, and `data\update.log`.

## Linux Version

A Linux-adapted version of HMP Panel is available for production server deployments:

- **Ubuntu 22.04/24.04 recommended**
- Runs the HappinessMP **Linux** server binary (`HappMP`)
- systemd service for automatic startup
- Pterodactyl egg included

👉 **[HMP Panel for Linux](https://github.com/zuraxscripts/hmp-panel)**

Key differences from the Windows version:

| Aspect | Windows | Linux |
| --- | --- | --- |
| Server binary | `HappMP.exe` | `HappMP` |
| Connector | `hpm-connector.dll` | `hpm-connector.so` |
| Virtual env | `.venv\Scripts\activate` | `source .venv/bin/activate` |
| Installer | `install.bat` one-click | Manual commands |
| Background run | `start_hidden.vbs` / Task Scheduler | systemd service |
| Start command | `start.bat` or `python main.py` | `python3 main.py` |
| Setup URL | Windows server zip | Linux server zip |
| Pterodactyl | Not supported | Egg included |

## Security Notes

| Area | Recommendation |
| --- | --- |
| Admin account | Use a strong password and keep admin users limited |
| Public exposure | Put the panel behind Windows Firewall rules or a reverse proxy |
| HTTPS | Use HTTPS when the panel is reachable over the internet (e.g. Nginx or Caddy on Windows) |
| Panel secret | Do not publish `panel_config.json` or connector `server.lua` |
| Database | Use a strong database password and restrict access to `127.0.0.1` |
| Permissions | Give non-admin users only the permissions they need |

## Troubleshooting

### "Python is not recognized" or "python is not found"

Reinstall Python from [python.org](https://www.python.org/downloads/) and make sure **"Add Python to PATH"** is checked during installation. Restart your terminal after installation.

### Panel does not start

Check:
- No other application is using port 20000
- You ran `install.bat` first (creates the virtual environment)
- Windows Firewall is not blocking Python
- If using XAMPP, make sure MySQL is started in the XAMPP Control Panel

### Setup cannot connect to the database

Make sure:
- MySQL/MariaDB is running (check XAMPP/WampServer control panel)
- The database exists and the user has privileges
- The host is correct (use `127.0.0.1` for local DB)
- The port is correct (default is `3306`)

### "Module not found" errors

Run `install.bat` again to reinstall dependencies.

### Console shows "detached process" or commands don't work

The server process might have been started externally or the stdin pipe was not connected. Restart the server from the panel to re-attach.

### Server shows wrong version

The panel downloads the version specified in `happiness_update.json`. Make sure that file points to the correct Windows server archive URL.

### How do I stop the panel?

Run **`stop_panel.bat`** or press `Ctrl+C` in the `start.bat` console window. For background mode, run `stop_panel.bat` or use Task Manager to end the Python processes.

### Can I run this on Linux?

No. Use the **[Linux version](https://github.com/zuraxscripts/hmp-panel)** instead.
