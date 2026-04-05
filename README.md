# [HappinessMP](https://happinessmp.net/) Panel

Web-based management panel for [HappinessMP](https://happinessmp.net/) servers.

It provides a browser UI for starting and stopping the server, live console access, file management, player management, resource and addon control, scheduled restarts, update checks, multi-user access, and Discord integration.

## Support Status

This project is intended for:

- Linux only
- `x86_64` / `amd64` only
- Ubuntu recommended

Not supported:

- Windows
- ARM / ARM64

If you already use **Pterodactyl Panel**, that is the recommended way to deploy this project. An egg is included in this repository:

- [`egg-hmp-happinessmp.json`](./egg-hmp-happinessmp.json)

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
- Automatic download of the Linux [HappinessMP](https://happinessmp.net/) server package during setup
- Automatic installation of `hpm-connector` during setup

## Requirements

Minimum practical requirements:

- Ubuntu 22.04 or 24.04
- Python 3.9+
- `git`
- `pip`
- A MySQL or MariaDB database
- Internet access during initial setup

Recommended:

- Ubuntu 24.04 LTS
- Python 3.11
- MariaDB
- Reverse proxy with Nginx
- `systemd` service for automatic startup

## How It Works

On first launch, the panel opens a setup flow in the browser and asks for:

1. Setup PIN shown in the console
2. Admin username and password
3. Database connection details

During setup, the panel will:

1. Save and validate the database connection
2. Create the required database tables
3. Download the [HappinessMP](https://happinessmp.net/) Linux server package
4. Install the latest `hpm-connector`
5. Update the connector configuration with the panel secret
6. Create your first admin account

By default, the game server executable ends up here:

```text
./HPNMP/HappMP
```

The web panel listens on port `20000` by default.

## Ubuntu Installation

### 1. Install system packages

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip mariadb-server
```

If you want a reverse proxy:

```bash
sudo apt install -y nginx
```

### 2. Create a database

Log into MariaDB:

```bash
sudo mysql
```

Create a database and user:

```sql
CREATE DATABASE happinessmp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'happinessmp'@'127.0.0.1' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON happinessmp.* TO 'happinessmp'@'127.0.0.1';
FLUSH PRIVILEGES;
EXIT;
```

If you need the panel to connect from another machine or container, create the user with the correct host instead of `127.0.0.1`.

### 3. Clone the repository

```bash
git clone https://github.com/zuraxscripts/hpm-panel.git
cd hpm-panel
```

### 4. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Start the panel

```bash
python3 main.py --port 20000
```

Then open:

```text
http://YOUR_SERVER_IP:20000
```

### 7. Complete first-time setup

When the panel starts for the first time, the console shows a 4-digit setup PIN. Open the web UI and finish the setup wizard:

1. Enter the setup PIN
2. Create the admin account
3. Enter the MariaDB/MySQL connection details
4. Wait for the panel to finish downloading and preparing the server

## Quick Start Commands

If you want the shortest full install flow on Ubuntu:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip mariadb-server
git clone https://github.com/zuraxscripts/hpm-panel.git
cd hpm-panel
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 main.py --port 20000
```

## Run on a Custom Port

You can start the panel on a different port:

```bash
python3 main.py --port 8080
```

You can also use environment variables:

```bash
PANEL_PORT=8080 python3 main.py
```

or:

```bash
PORT=8080 python3 main.py
```

## Firewall Example

If `ufw` is enabled:

```bash
sudo ufw allow 20000/tcp
sudo ufw reload
```

## Run as a systemd Service

Create a dedicated user:

```bash
sudo useradd -r -m -s /usr/sbin/nologin hpm
```

Clone the project:

```bash
sudo mkdir -p /opt/hpm-panel
sudo chown -R hpm:hpm /opt/hpm-panel
sudo -u hpm git clone https://github.com/zuraxscripts/hpm-panel.git /opt/hpm-panel/app
```

Create the virtual environment and install dependencies:

```bash
sudo -u hpm python3 -m venv /opt/hpm-panel/app/.venv
sudo -u hpm /opt/hpm-panel/app/.venv/bin/pip install --upgrade pip
sudo -u hpm /opt/hpm-panel/app/.venv/bin/pip install -r /opt/hpm-panel/app/requirements.txt
```

Create the service file:

```bash
sudo nano /etc/systemd/system/hpm-panel.service
```

Use:

```ini
[Unit]
Description=HMP Panel
After=network.target mariadb.service

[Service]
Type=simple
User=hpm
Group=hpm
WorkingDirectory=/opt/hpm-panel/app
Environment=PANEL_PORT=20000
ExecStart=/opt/hpm-panel/app/.venv/bin/python /opt/hpm-panel/app/main.py --port 20000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hpm-panel
sudo systemctl status hpm-panel
```

View logs:

```bash
journalctl -u hpm-panel -f
```

## Reverse Proxy Example with Nginx

Install Nginx if needed:

```bash
sudo apt install -y nginx
```

Create a site:

```bash
sudo nano /etc/nginx/sites-available/hpm-panel
```

Example config:

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

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/hpm-panel /etc/nginx/sites-enabled/hpm-panel
sudo nginx -t
sudo systemctl reload nginx
```

If you use HTTPS behind a reverse proxy, these environment variables may be useful:

```bash
PANEL_FORCE_HTTPS=true
PANEL_SESSION_COOKIE_SECURE=true
```

## Environment Variables

Optional runtime variables:

```bash
PANEL_PORT=20000
PORT=20000
PANEL_PRODUCTION=true
PANEL_ACCESS_LOGS=false
PANEL_FORCE_HTTPS=false
PANEL_SESSION_COOKIE_SECURE=false
PANEL_SOCKETIO_ASYNC_MODE=threading
```

Optional database variables:

```bash
HAPPINESS_DB_HOST=127.0.0.1
HAPPINESS_DB_PORT=3306
HAPPINESS_DB_USER=happinessmp
HAPPINESS_DB_PASSWORD=CHANGE_ME
HAPPINESS_DB_NAME=happinessmp
```

If the `HAPPINESS_DB_*` variables are set, the panel can load database settings from the environment instead of the local DB config file.

## Important Files and Directories

- [`main.py`](./main.py) - Launcher
- [`server_manager.py`](./server_manager.py) - Main web panel server
- [`updater.py`](./updater.py) - Built-in updater worker
- [`requirements.txt`](./requirements.txt) - Python dependencies
- [`egg-hmp-happinessmp.json`](./egg-hmp-happinessmp.json) - Pterodactyl egg
- `panel_config.json` - Panel configuration
- [`update_config.json`](./update_config.json) - Update source configuration
- [`happiness_update.json`](./happiness_update.json) - [HappinessMP](https://happinessmp.net/) update metadata
- `data/` - Runtime data, logs, DB config, update state
- `HPNMP/` - Downloaded [HappinessMP](https://happinessmp.net/) server files
- [`templates/`](./templates) - HTML templates and static assets
- [`locales/`](./locales) - UI translations

## Default Paths

Important defaults used by the project:

- Panel port: `20000`
- Game server executable: `./HPNMP/HappMP`
- Game server directory: `./HPNMP/`
- Logs directory: `./data/logs/`

## Pterodactyl Panel

If you already run **Pterodactyl**, this is the recommended deployment method.

The repository includes a ready egg:

- [`egg-hmp-happinessmp.json`](./egg-hmp-happinessmp.json)

### What the egg does

- Installs `git`, `curl`, and `python3`
- Clones this repository into the server directory
- Starts the panel with:

```bash
python3 main.py --port {{PORT}}
```

### Importing the egg

Import the JSON file into your Pterodactyl panel and create a server from that egg. The egg exposes:

- `PORT`

After the server starts, open the allocated port in your browser and complete the same web setup flow described above.

### Pterodactyl notes

- Linux only
- `amd64` / `x86_64` only
- Not supported on Windows nodes
- Not supported on ARM nodes
- The panel still needs a working MySQL/MariaDB database
- The first setup still needs outbound internet access to download [HappinessMP](https://happinessmp.net/) files and `hpm-connector`

## Updating

The panel includes an update system for:

- The panel itself
- [HappinessMP](https://happinessmp.net/) server files

By default, update metadata is read from:

- [`update_config.json`](./update_config.json)
- [`happiness_update.json`](./happiness_update.json)

You can also trigger update checks from the web panel.

## Security Notes

- Use a strong admin password
- Do not expose the panel publicly without proper firewall or reverse proxy rules
- Use HTTPS when exposing the panel to the internet
- Protect the generated panel secret
- Give only the permissions needed to non-admin users

## Troubleshooting

### The panel does not open

Check that the service is running and the port is open:

```bash
ss -tulpn | grep 20000
```

### Setup cannot connect to the database

Make sure:

- MariaDB/MySQL is running
- The database already exists
- The username, password, host, and port are correct
- The DB user has privileges on the selected database

Quick check:

```bash
mysql -h 127.0.0.1 -u happinessmp -p happinessmp
```

### The server executable is missing

The panel expects the Linux server binary at:

```text
./HPNMP/HappMP
```

If setup did not finish correctly, start the panel again and complete the setup flow.

### WebSocket or live console issues behind Nginx

Make sure your reverse proxy passes:

- `Upgrade`
- `Connection`

The example Nginx config above already includes that.

### Running on Windows or ARM

That is not supported for this project.

## Notes

This repository is focused on [HappinessMP](https://happinessmp.net/) server management on Linux. If you want the easiest deployment path and already use Pterodactyl, use the included egg and keep the panel behind proper network rules.
