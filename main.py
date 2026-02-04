#!/usr/bin/env python3
"""
HappinessMP Server Manager - Single Entry Point
Handles dependency installation and starts all services.
Designed to run on Pterodactyl Python egg.
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path

REQUIREMENTS_FILE = "requirements.txt"

processes = []
RESTART_FLAG = Path("data") / "restart.flag"


def install_dependencies():
    """Install packages from requirements.txt if needed."""
    if not os.path.exists(REQUIREMENTS_FILE):
        print("[WARN] requirements.txt not found, skipping install")
        return

    print("[INFO] Checking / installing dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE,
         "--quiet", "--disable-pip-version-check"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("[OK]   Dependencies ready")
    else:
        print("[WARN] pip exited with code", result.returncode)
        if result.stderr:
            print(result.stderr.strip())
        print("[INFO] Continuing anyway...")


def shutdown(signum=None, frame=None):
    """Stop all child processes."""
    print("\n[INFO] Stopping services...")
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
    # Give them a moment to exit gracefully
    for proc in processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("[OK]   All services stopped")
    if RESTART_FLAG.exists():
        try:
            RESTART_FLAG.unlink()
        except Exception:
            pass
        print("[INFO] Restart flag detected, restarting...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    sys.exit(0)


def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("=" * 55)
    print("  HappinessMP Server Manager")
    print("=" * 55)
    print()

    # Step 1: Install dependencies
    install_dependencies()
    print()

    # Step 2: Start SFTP server
    print("[INFO] Starting SFTP Server...")
    sftp_proc = subprocess.Popen(
        [sys.executable, "sftp_server.py"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    processes.append(sftp_proc)

    # Small delay so SFTP binds its port before web panel starts
    time.sleep(2)

    # Step 3: Start Web Control Panel
    print("[INFO] Starting Web Control Panel...")
    web_proc = subprocess.Popen(
        [sys.executable, "server_manager.py"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    processes.append(web_proc)

    print()
    print("=" * 55)
    print("  Services Started!")
    print()
    print("  Web Panel:    http://0.0.0.0:8080")
    print("  SFTP Server:  See user ports in config")
    print()
    print("  Press Ctrl+C to stop all services")
    print("=" * 55)
    print()

    # Step 4: Wait for processes - if either exits, shut everything down
    try:
        while True:
            for proc in processes:
                ret = proc.poll()
                if ret is not None:
                    print(f"[WARN] Process (pid {proc.pid}) exited with code {ret}")
                    shutdown()
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        shutdown()


if __name__ == "__main__":
    main()
