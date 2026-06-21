<div align="center">
  <img src="templates/logo.png" alt="HappinessMP logo" width="160" />

  <h1>HMP Panel</h1>

  <p><strong>Web control panel for HappinessMP servers on Linux.</strong></p>

  <p>
    Start the server, watch the console, edit files, manage players, schedule restarts,
    sync the hpm-connector bridge, and keep panel/HappinessMP updates in one browser UI.
  </p>

  <p>
    <img alt="Linux x86_64 target" src="https://img.shields.io/badge/Target-Linux%20x86__64-101827?style=for-the-badge&logo=linux&logoColor=white">
    <img alt="Python 3.9+" src="https://img.shields.io/badge/Python-3.9%2B-2563eb?style=for-the-badge&logo=python&logoColor=white">
    <img alt="MySQL/MariaDB" src="https://img.shields.io/badge/Database-MySQL%2FMariaDB-16a34a?style=for-the-badge">
    <img alt="Pterodactyl egg included" src="https://img.shields.io/badge/Pterodactyl-egg%20included-f59e0b?style=for-the-badge">
  </p>

  <p>
    <a href="#what-it-does">What It Does</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#quick-start">Quick Start</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#first-run">First Run</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#pterodactyl">Pterodactyl</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#configuration">Configuration</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#windows-version">Windows Version</a>
    <span>&nbsp;/&nbsp;</span>
    <a href="#troubleshooting">Troubleshooting</a>
  </p>
</div>

---

> [!IMPORTANT]
> HMP Panel targets Linux `x86_64` / `amd64` HappinessMP server deployments. For Windows, see the <a href="#windows-version">Windows Version</a> section.

> [!NOTE]
> HMP Panel requires MySQL or MariaDB for data storage.

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
| Setup | PIN-protected first run, admin account creation, HappinessMP server download, hpm-connector installation |
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
| Pterodactyl | Ready-to-import egg with Debian-based Python container |

## Requirements

| Requirement | Notes |
| --- | --- |
| OS | Linux (Ubuntu 22.04/24.04 recommended) |
| Architecture | `x86_64` / `amd64` |
| Python | `3.9+` (3.11+ recommended) |
| Database | MySQL or MariaDB server |
| Python packages | Installed from [`requirements.txt`](./requirements.txt) |
| Tools | `git`, `python3`, `python3-venv`, `python3-pip` |
| Network | Needed during first setup to download the HappinessMP Linux server archive |
| Internet | Required for update checks and hpm-connector downloads |

## Quick Start

```bash
# 1. Install system packages
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip mariadb-server

# 2. Create a database
sudo mysql -e "CREATE DATABASE happinessmp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER 'happinessmp'@'127.0.0.1' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';"
sudo mysql -e "GRANT ALL PRIVILEGES ON happinessmp.* TO 'happinessmp'@'127.0.0.1';"
sudo mysql -e "FLUSH PRIVILEGES;"

# 3. Clone and install
git clone -b linux https://github.com/zuraxscripts/hmp-panel.git
cd hmp-panel
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Start the panel
python3 main.py --port 20000
```

Open the panel:

```text
http://YOUR_SERVER_IP:20000
```

## First Run

The first launch is protected by a setup PIN printed in the console.

Setup asks for:

1. Setup PIN from the terminal
2. Admin username and password
3. Database connection details (host, port, user, password, database)

Setup then performs:

| Step | Result |
| --- | --- |
| Database | Saves encrypted DB credentials and creates required tables |
| Secret | Generates the panel secret if still using the default |
| Server files | Downloads the official HappinessMP Linux x64 archive when missing |
| hpm-connector | Downloads and installs the latest connector release |
| Config | Updates connector config with the panel secret and host |
| User | Creates the first admin account |

Default paths:

| Item | Value |
| --- | --- |
| Panel port | `20000` |
| Server executable | `./HPNMP/HappMP` |
| Server directory | `./HPNMP/` |
| Panel config | `./panel_config.json` |
| Runtime data | `./data/` |
| Logs | `./data/logs/` |

## Ubuntu Service

Create a dedicated user:

```bash
sudo useradd -r -m -s /usr/sbin/nologin hpm
```

Install the app:

```bash
sudo mkdir -p /opt/hmp-panel
sudo chown -R hpm:hpm /opt/hmp-panel
sudo -u hpm git clone -b linux https://github.com/zuraxscripts/hmp-panel.git /opt/hmp-panel/app
sudo -u hpm python3 -m venv /opt/hmp-panel/app/.venv
sudo -u hpm /opt/hmp-panel/app/.venv/bin/pip install --upgrade pip
sudo -u hpm /opt/hmp-panel/app/.venv/bin/pip install -r /opt/hmp-panel/app/requirements.txt
```

Create `/etc/systemd/system/hmp-panel.service`:

```ini
[Unit]
Description=HMP Panel
After=network.target mariadb.service

[Service]
Type=simple
User=hpm
Group=hpm
WorkingDirectory=/opt/hmp-panel/app
Environment=PANEL_PORT=20000
ExecStart=/opt/hmp-panel/app/.venv/bin/python /opt/hmp-panel/app/main.py --port 20000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hmp-panel
sudo systemctl status hmp-panel
```

Follow logs:

```bash
journalctl -u hmp-panel -f
```

## Nginx Reverse Proxy

HMP Panel uses Socket.IO, so the proxy must pass WebSocket upgrade headers.

```nginx
server {
    listen 80;
    server_name panel.example.com;

    location / {
        proxy_pass http://127.0.0.1:20000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Useful environment flags behind HTTPS:

```bash
PANEL_FORCE_HTTPS=true
PANEL_SESSION_COOKIE_SECURE=true
```

## Pterodactyl

Use the included egg when deploying through Pterodactyl:

| File | Purpose |
| --- | --- |
| [`egg-hmp-happinessmp.json`](./egg-hmp-happinessmp.json) | Ready-to-import Pterodactyl egg |

The egg does the following:

| Step | Details |
| --- | --- |
| Install | Installs `git`, `curl`, and `python3` via `apt` |
| Clone | Clones this repository |
| Startup | Starts `python3 main.py --port {{PORT}}` |

Important Pterodactyl notes:

| Topic | Note |
| --- | --- |
| Architecture | Use Linux `amd64` / `x86_64` nodes |
| External database | Required (MySQL/MariaDB) |
| Internet | First setup needs outbound access for HappinessMP files and hpm-connector |
| Windows nodes | Not supported |

## Configuration

### CLI and Environment

```bash
python3 main.py --port 20000
```

The panel port can also come from environment variables:

```bash
PANEL_PORT=20000 python3 main.py
PORT=20000 python3 main.py
```

Runtime environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PANEL_PORT` / `PORT` | `20000` | Panel HTTP port |
| `PANEL_PRODUCTION` | `true` | Enables production defaults |
| `PANEL_ACCESS_LOGS` | `false` in production | Controls HTTP access logging |
| `PANEL_FORCE_HTTPS` | `false` | Redirects HTTP to HTTPS when enabled |
| `PANEL_SESSION_COOKIE_SECURE` | follows HTTPS flag | Marks session cookie secure |
| `PANEL_SOCKETIO_ASYNC_MODE` | auto/threading | Forces Socket.IO async backend |
| `HAPPINESS_DB_HOST` | `127.0.0.1` | Database server host |
| `HAPPINESS_DB_PORT` | `3306` | Database server port |
| `HAPPINESS_DB_USER` | `happinessmp` | Database user |
| `HAPPINESS_DB_PASSWORD` | — | Database password |
| `HAPPINESS_DB_NAME` | `happinessmp` | Database name |
| `HPM_UPDATE_CONFIG_URL` | empty | Optional remote update config JSON |
| `HPM_PANEL_REPO` | `zuraxscripts/hmp-panel` | GitHub repo for panel update checks |
| `HPM_HAPPINESS_UPDATE_URL` | default | HappinessMP update metadata URL override |
| `HPM_UPDATE_INTERVAL_MINUTES` | `10` | Background update check interval |

### Repository Files

| Path | Purpose |
| --- | --- |
| [`main.py`](./main.py) | Launcher, dependency check, child process supervision |
| [`server_manager.py`](./server_manager.py) | Flask/Socket.IO panel, routes, setup, server control |
| [`storage.py`](./storage.py) | Storage layer (MySQL + JSON fallback) |
| [`db.py`](./db.py) | Database connection, encrypted credentials, schema |
| [`updater.py`](./updater.py) | Panel and HappinessMP updater worker |
| [`requirements.txt`](./requirements.txt) | Python dependencies |
| [`panel_version.json`](./panel_version.json) | Current panel version |
| [`update_config.json`](./update_config.json) | Default update sources |
| [`happiness_update.json`](./happiness_update.json) | HappinessMP update metadata |
| [`egg-hmp-happinessmp.json`](./egg-hmp-happinessmp.json) | Pterodactyl egg |
| [`templates/`](./templates) | Panel pages and UI assets |
| [`locales/`](./locales) | English and Czech translations |

## In-Game Bridge

During setup, HMP Panel installs the hpm-connector bridge package:

| Component | Location | Purpose |
| --- | --- | --- |
| hpm-connector | `HPNMP/resources/hpm-connector/` | Sends player sync, heartbeat, and receives pending actions |
| Resource config | `HPNMP/settings.xml` | Updated to load the connector resource |

The bridge uses a generated `panelSecret` stored in `panel_config.json` and mirrored into the connector's `server.lua`.

## Updating

HMP Panel can check and apply updates for:

| Target | Source |
| --- | --- |
| Panel | GitHub repository from `update_config.json` or `HPM_PANEL_REPO` |
| HappinessMP server | Archive URL from `happiness_update.json` or `HPM_HAPPINESS_UPDATE_URL` |

The updater stores state in `data/update_status.json`, `data/update_job.json`, and `data/update.log`.

## Security Notes

| Area | Recommendation |
| --- | --- |
| Admin account | Use a strong password and keep admin users limited |
| Public exposure | Put the panel behind firewall rules or a reverse proxy |
| HTTPS | Use HTTPS when the panel is reachable over the internet |
| Panel secret | Do not publish `panel_config.json` or connector `server.lua` |
| Database | Use a strong database password and restrict access to `127.0.0.1` |
| Permissions | Give non-admin users only the permissions they need |

## Windows Version

A Windows-adapted version of HMP Panel is available:

- **Windows 10/11 and Windows Server 2019+**
- Runs the HappinessMP **Windows** server binary (`HappMP.exe`)
- Uses `.bat` scripts for installation and startup
- Same features as the Linux version

👉 **[HMP Panel for Windows](https://github.com/zuraxscripts/hmp-panel/tree/windows)**

Key differences from the Linux version:

| Aspect | Linux | Windows |
| --- | --- | --- |
| Server binary | `HappMP` | `HappMP.exe` |
| Connector | `hpm-connector.so` | `hpm-connector.dll` |
| Virtual env | `source .venv/bin/activate` | `.venv\Scripts\activate` |
| Installer | Manual commands | `install.bat` one-click |
| Background run | systemd service | `start_hidden.vbs` |
| Start command | `python3 main.py` | `start.bat` or `python main.py` |
| Setup URL | Linux server zip | Windows server zip |

## Troubleshooting

### Panel does not open

Check whether the process is listening:

```bash
ss -tulpn | grep 20000
```

Check service logs if using systemd:

```bash
journalctl -u hmp-panel -f
```

### Setup cannot connect to the database

Make sure:

- MariaDB/MySQL is running
- The database exists
- The username, password, host, and port are correct
- The DB user has privileges on the selected database

Quick check:

```bash
mysql -h 127.0.0.1 -u happinessmp -p happinessmp
```

### Server executable is missing

The default path is:

```text
./HPNMP/HappMP
```

If the file is missing, rerun setup or check whether outbound downloads from the HappinessMP CDN are blocked.

### WebSocket/live console issues behind Nginx

Confirm the proxy passes these headers:

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### Running on Windows

This Linux version does not support Windows. Use the **[Windows version](https://github.com/zuraxscripts/hmp-panel/tree/windows)** instead.

### Running on ARM

ARM / ARM64 architectures are not supported.
