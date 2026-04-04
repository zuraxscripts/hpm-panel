"""
HappinessMP Server Manager - Single Entry Point
Handles dependency installation and starts all services.
Designed to run on Pterodactyl Python egg.
"""

import argparse
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

REQUIREMENTS_FILE = "requirements.txt"
DEFAULT_PANEL_PORT = 20000

processes = []
RESTART_FLAG = Path("data") / "restart.flag"


def _parse_port(value):
    try:
        port = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("Port must be an integer")
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535")
    return port


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
    parser = argparse.ArgumentParser(description="HappinessMP panel launcher")
    parser.add_argument(
        "--port",
        type=_parse_port,
        default=DEFAULT_PANEL_PORT,
        help=f"Panel HTTP port (default: {DEFAULT_PANEL_PORT})",
    )
    args = parser.parse_args()

                              
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("=" * 55)
    print("  HappinessMP Server Manager")
    print("=" * 55)
    print()

                                  
    install_dependencies()
    print()

                                     
    print(f"[INFO] Starting Web Control Panel on port {args.port}...")
    web_proc = subprocess.Popen(
        [sys.executable, "server_manager.py", "--port", str(args.port)],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    processes.append(web_proc)

    print()
    print("=" * 55)
    print("  Services Started!")
    print()
    print("  Press Ctrl+C to stop all services")
    print("=" * 55)
    print()

                                                                        
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
