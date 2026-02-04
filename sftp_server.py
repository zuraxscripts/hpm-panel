#!/usr/bin/env python3
"""
SFTP Server (per-user) for HappinessMP file management

- Reads users from ./data/users.json (same as server_manager.py)
- Starts one SFTP listener per user on their assigned port (user['sftp_port'])
- Password = account password (verified against werkzeug password hash)
- Root directory = directory containing the server executable from ./data/config.json
"""

import os
import json
import time
import socket
import threading
import logging
from pathlib import Path

import paramiko
from paramiko import (
    ServerInterface,
    SFTPServerInterface,
    SFTPServer,
    SFTPAttributes,
    SFTP_OK,
    SFTP_NO_SUCH_FILE,
    SFTP_PERMISSION_DENIED,
    SFTP_FAILURE,
)
from paramiko.sftp_handle import SFTPHandle
from werkzeug.security import check_password_hash
import storage

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ---------------- Paths ----------------
DATA_DIR = Path("./data")
USERS_FILE = DATA_DIR / "users.json"
CONFIG_FILE = DATA_DIR / "config.json"
HOSTKEY_FILE = DATA_DIR / "sftp_hostkey_rsa.pem"

DATA_DIR.mkdir(exist_ok=True)


def load_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {path}: {e}")
    return default


def load_config():
    try:
        return storage.load_config()
    except Exception:
        return load_json(
            CONFIG_FILE,
            {
                "server_path": "/root/Plocha/MP",  # Set this to the path you want as root
                "sftp_base_port": 2222,
            },
        )


def load_users():
    try:
        return storage.load_users()
    except Exception:
        return load_json(USERS_FILE, {})


def get_server_root_dir(config: dict) -> str:
    server_path = config.get("server_path", "/root/Plocha/MP")
    server_path = os.path.abspath(server_path)
    return server_path


def load_or_create_hostkey():
    """Use a persistent host key so clients don't get 'host key changed' warnings after restart."""
    if HOSTKEY_FILE.exists():
        try:
            return paramiko.RSAKey.from_private_key_file(str(HOSTKEY_FILE))
        except Exception as e:
            logging.error(f"Failed to read host key, will regenerate: {e}")

    try:
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(str(HOSTKEY_FILE))
        os.chmod(HOSTKEY_FILE, 0o600)
        logging.info(f"Generated new host key: {HOSTKEY_FILE}")
        return key
    except Exception as e:
        logging.error(f"Failed to generate host key: {e}")
        return paramiko.RSAKey.generate(2048)


class UserSSHServer(ServerInterface):
    """ServerInterface that authenticates one concrete user (username) on one port."""

    def __init__(self, username: str):
        self.username = username

    def check_auth_password(self, username, password):
        users = load_users()
        user = users.get(self.username)

        if not user:
            return paramiko.AUTH_FAILED

        if username != self.username:
            return paramiko.AUTH_FAILED

        if not user.get("enabled", True):
            return paramiko.AUTH_FAILED

        perms = user.get("permissions", {})
        if perms.get("can_use_sftp", True) is not True:
            return paramiko.AUTH_FAILED

        try:
            if check_password_hash(user["password"], password):
                return paramiko.AUTH_SUCCESSFUL
        except Exception:
            return paramiko.AUTH_FAILED

        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password"


class FSHandle(SFTPHandle):
    """
    File handle wrapper.
    Paramiko can use .readfile/.writefile if set, but we also keep stat reliable.
    """

    def stat(self):
        try:
            f = self.readfile or self.writefile
            if not f:
                return SFTP_FAILURE
            return SFTPAttributes.from_stat(os.fstat(f.fileno()))
        except FileNotFoundError:
            return SFTP_NO_SUCH_FILE
        except PermissionError:
            return SFTP_PERMISSION_DENIED
        except Exception:
            return SFTP_FAILURE


class RootedSFTP(SFTPServerInterface):
    """SFTP implementation with root jail (server_root)."""

    def __init__(self, server, server_root: str, username: str, *args, **kwargs):
        self.server_root = os.path.abspath(server_root)
        self.username = username  # Added username to RootedSFTP
        super().__init__(server, *args, **kwargs)

    def _jail_ok(self, real_path: str) -> bool:
        """Check if the real_path is within the root folder."""
        try:
            return os.path.commonpath([self.server_root, real_path]) == self.server_root
        except Exception:
            return False

    def _realpath(self, path: str) -> str:
        """Convert virtual path to real file system path, and ensure it's within the root folder."""
        if path in ("", ".", None):
            return self.server_root

        if isinstance(path, bytes):
            path = path.decode("utf-8", errors="ignore")

        if path.startswith("/"):
            path = path[1:]

        # Prevent traversing out of the allowed root folder
        real_path = os.path.abspath(os.path.normpath(os.path.join(self.server_root, path)))

        if not self._jail_ok(real_path):
            return self.server_root  # Prevent access to paths outside the allowed root

        return real_path

    def realpath(self, path):
        """Convert path to real path, and map back to virtual path relative to the root."""
        if path in (".", "", None):
            return "/"
        real = self._realpath(path)
        if real == self.server_root:
            return "/"
        rel = os.path.relpath(real, self.server_root).replace("\\", "/")
        return "/" + rel

    def list_folder(self, path):
        """List the contents of a folder, but ensure we stay within the allowed root directory."""
        try:
            real = self._realpath(path)
            out = []
            for fname in os.listdir(real):
                full = os.path.join(real, fname)
                st = os.stat(full)
                attr = SFTPAttributes.from_stat(st)
                attr.filename = fname
                out.append(attr)
            return out
        except FileNotFoundError:
            return SFTP_NO_SUCH_FILE
        except PermissionError:
            return SFTP_PERMISSION_DENIED
        except Exception as e:
            logging.warning(f"[SFTP] list_folder error path={path!r}: {e}")
            return SFTP_FAILURE

    def stat(self, path):
        """Get the status of a file."""
        try:
            return SFTPAttributes.from_stat(os.stat(self._realpath(path)))
        except FileNotFoundError:
            return SFTP_NO_SUCH_FILE
        except PermissionError:
            return SFTP_PERMISSION_DENIED
        except Exception as e:
            logging.warning(f"[SFTP] stat error path={path!r}: {e}")
            return SFTP_FAILURE

    def open(self, path, flags, attr):
        """Open a file or directory, ensuring we don't allow going outside the root directory."""
        try:
            real = self._realpath(path)
            parent = os.path.dirname(real)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)

            # Choose file opening mode based on flags
            mode = "rb"
            if flags & os.O_WRONLY:
                mode = "ab" if (flags & os.O_APPEND) else "wb"
            elif flags & os.O_RDWR:
                mode = "a+b" if (flags & os.O_APPEND) else "r+b"

            f = open(real, mode)

            h = FSHandle(flags)
            h.filename = real
            h.readfile = f
            h.writefile = f
            return h

        except FileNotFoundError:
            return SFTP_NO_SUCH_FILE
        except PermissionError as e:
            logging.warning(f"[SFTP] open PERMISSION path={path!r} real={self._realpath(path)!r}: {e}")
            return SFTP_PERMISSION_DENIED
        except Exception as e:
            logging.warning(f"[SFTP] open FAIL path={path!r} real={self._realpath(path)!r}: {e}")
            return SFTP_FAILURE


def serve_user_sftp(username: str, port: int, host_key, server_root: str):
    """One SFTP listener per user on a dedicated port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("0.0.0.0", int(port)))
        sock.listen(50)
    except Exception as e:
        logging.error(f"[SFTP] {username}: failed to bind port {port}: {e}")
        return

    logging.info(f"[SFTP] {username}: listening on 0.0.0.0:{port} (root={server_root})")

    while True:
        transport = None
        try:
            conn, addr = sock.accept()
            transport = paramiko.Transport(conn)
            transport.add_server_key(host_key)

            ssh_server = UserSSHServer(username=username)

            transport.set_subsystem_handler(
                "sftp",
                SFTPServer,
                lambda server, *a, **k: RootedSFTP(server, server_root, username, *a, **k),
            )

            transport.start_server(server=ssh_server)

            chan = transport.accept(20)
            if chan is None:
                transport.close()
                continue

            while transport.is_active():
                time.sleep(0.1)

            transport.close()

        except Exception as e:
            logging.warning(f"[SFTP] {username}: client error: {e}")
            try:
                if transport:
                    transport.close()
            except Exception:
                pass


def main():
    config = load_config()
    server_root_default = get_server_root_dir(config)
    users = load_users()

    if not users:
        logging.error("No users found in ./data/users.json. Create users via manager first.")
        return

    host_key = load_or_create_hostkey()

    started = 0
    for username, u in users.items():
        if not u.get("enabled", True):
            continue

        perms = u.get("permissions", {})
        if perms.get("can_use_sftp", True) is not True:
            continue

        port = u.get("sftp_port")
        if not port:
            continue

        server_root = server_root_default

        # This will set the root folder to "/root/Plocha/MP"
        if username.lower() == "zurax":
            server_root = "/root/Plocha/"

        t = threading.Thread(
            target=serve_user_sftp,
            args=(username, int(port), host_key, server_root),
            daemon=True,
        )
        t.start()
        started += 1

    if started == 0:
        logging.warning("No SFTP listeners started (no enabled users with can_use_sftp + sftp_port).")
    else:
        logging.info(f"Started {started} per-user SFTP listeners.")

    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
