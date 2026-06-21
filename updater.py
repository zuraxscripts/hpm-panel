import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
USER_AGENT = 'HPM-Panel-Updater/1.0'
DATA_DIR = ROOT_DIR / 'data'
STATUS_FILE = DATA_DIR / 'update_status.json'
LOG_FILE = DATA_DIR / 'update.log'
DEFAULT_PANEL_PORT = 20000
PANEL_PORT = DEFAULT_PANEL_PORT
CONNECTOR_API_URL = 'https://api.github.com/repos/zuraxscripts/hmp-connector/releases/latest'

DATA_DIR.mkdir(exist_ok=True)

IS_WINDOWS = (os.name == 'nt')
SERVER_BINARY = 'HappMP.exe' if IS_WINDOWS else 'HappMP'
SERVER_BIN_SRC = 'HappinessMP.Server.exe' if IS_WINDOWS else 'HappinessMP.Server.out'


STATUS_TEMPLATE = {
    'running': False,
    'finished': False,
    'success': False,
    'progress': 0,
    'step': '',
    'message': '',
    'targets': [],
    'error': '',
    'log': [],
    'updated_at': None
}


_status = dict(STATUS_TEMPLATE)


def _coerce_panel_port(value):
    try:
        port = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("Port must be an integer")
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535")
    return port


def _resolve_panel_port(job):
    port = job.get('panel_port')
    if port:
        try:
            return _coerce_panel_port(port)
        except Exception:
            pass
    return DEFAULT_PANEL_PORT


def _load_server_config():
    cfg_path = ROOT_DIR / 'data' / 'config.json'
    try:
        if cfg_path.exists():
            return json.loads(cfg_path.read_text(encoding='utf-8'))
    except Exception:
        pass
    return {}


def _load_panel_config():
    cfg_path = ROOT_DIR / 'panel_config.json'
    try:
        if cfg_path.exists():
            return json.loads(cfg_path.read_text(encoding='utf-8'))
    except Exception:
        pass
    return {}


def _write_status():
    _status['updated_at'] = time.time()
    try:
        STATUS_FILE.write_text(json.dumps(_status, indent=2), encoding='utf-8')
    except Exception:
        pass


def _set_status(**kw):
    for k, v in kw.items():
        _status[k] = v
    _write_status()


def _log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    _status['log'].append(line)
    _write_status()
    print(line, flush=True)


def _download_with_progress(url, dest, start_pct, end_pct, label='file'):
    _log(f'Downloading {label} from {url}...')
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        total = int(resp.headers.get('content-length', 0))
        downloaded = 0
        chunk_size = 8192
        with open(dest, 'wb') as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = start_pct + (end_pct - start_pct) * downloaded // total
                    _set_status(progress=min(pct, end_pct))
    _log(f'{label} downloaded')


def _find_file(root: Path, target_name: str):
    for p in root.rglob(target_name):
        if p.name == target_name:
            return p
    return None


def _merge_server_tree(src_root: Path, dst_root: Path):
    if not dst_root.exists():
        dst_root.mkdir(parents=True, exist_ok=True)
    for item in src_root.iterdir():
        dest = dst_root / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(item, dest)
        else:
            if dest.exists():
                dest.unlink()
            shutil.copy2(item, dest)


def _update_happiness_info(version, zip_url):
    info = {'version': version, 'zip_url': zip_url}
    try:
        (ROOT_DIR / 'happiness_update.json').write_text(
            json.dumps(info, indent=4), encoding='utf-8')
    except Exception:
        pass


def _load_happiness_local_info():
    try:
        p = ROOT_DIR / 'happiness_update.json'
        if p.exists():
            return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        pass
    return {}


def _install_connector(server_dir: Path):
    _log('Downloading latest hpm-connector...')
    try:
        req = urllib.request.Request(CONNECTOR_API_URL, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        raise RuntimeError(f'Failed to fetch connector release info: {e}')

    assets = data.get('assets', [])
    zip_asset = None
    for a in assets:
        name = a.get('name', '')
        if name.endswith('.zip'):
            zip_asset = a
            break
    if not zip_asset:
        raise RuntimeError('No zip asset found in connector release')

    zip_url = zip_asset['browser_download_url']
    tmpdir = Path(tempfile.mkdtemp())
    zip_path = tmpdir / 'connector.zip'
    _download_with_progress(zip_url, zip_path, 0, 0, 'hpm-connector')

    extract_dir = tmpdir / 'connector_extract'
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_dir)

    resources_dir = server_dir / 'resources'
    resources_dir.mkdir(exist_ok=True)

    connector_dll_name = 'hpm-connector.dll' if IS_WINDOWS else 'hpm-connector.so'
    connector_dll = _find_file(extract_dir, connector_dll_name)
    if not connector_dll:
        raise RuntimeError(f'{connector_dll_name} not found in connector package')

    dest_dll = resources_dir / connector_dll.name
    if dest_dll.exists():
        dest_dll.unlink()
    shutil.copy2(connector_dll, dest_dll)
    _log(f'Connector installed to {dest_dll}')

    connector_zip_path = resources_dir / 'hpm-connector.zip'
    if connector_zip_path.exists():
        connector_zip_path.unlink()

    shutil.rmtree(tmpdir, ignore_errors=True)


def _update_happiness(job: dict):
    _log('Starting HappinessMP update...')
    _set_status(step='HappinessMP', progress=5)

    happiness_info = job.get('happiness_info', {})
    happiness_version = happiness_info.get('version', '')
    happiness_zip_url = happiness_info.get('zip_url', '')

    if not happiness_zip_url:
        raise RuntimeError('No HappinessMP zip_url in update job')

    start_pct = 10
    span = 80
    end_pct = start_pct + span

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        zip_path = tmpdir / 'happiness_update.zip'
        dl_end = start_pct + int(span * 0.6)
        extract_end = start_pct + int(span * 0.75)
        _set_status(step='HappinessMP', progress=start_pct)
        _download_with_progress(happiness_zip_url, zip_path, start_pct, dl_end, 'HappinessMP files')

        extract_dir = tmpdir / 'server_extract'
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)
        _set_status(progress=extract_end)

        server_bin = _find_file(extract_dir, SERVER_BIN_SRC)
        if not server_bin:
            raise RuntimeError(f'{SERVER_BIN_SRC} not found in extracted server files')

        server_root = server_bin.parent
        server_cfg = _load_server_config()
        server_path = server_cfg.get('server_path', f'./HPNMP/{SERVER_BINARY}')
        server_dir = Path(server_path).resolve().parent
        if not server_dir.exists():
            raise RuntimeError(f'Server directory not found: {server_dir}')

        _log('Updating server files...')
        _merge_server_tree(server_root, server_dir)

        src = server_dir / SERVER_BIN_SRC
        dst = server_dir / SERVER_BINARY
        if src.exists():
            if dst.exists():
                dst.unlink()
            src.rename(dst)
        if dst.exists():
            if not IS_WINDOWS:
                try:
                    os.chmod(dst, 0o755)
                except Exception:
                    pass

    _log('Reinstalling hpm-connector...')
    _install_connector(server_dir)

    panel_cfg = _load_panel_config()
    panel_secret = panel_cfg.get('panel_secret') or ''
    if panel_secret:
        try:
            _update_connector_config(server_dir, panel_secret, _get_panel_host())
        except Exception:
            pass
    try:
        _ensure_connector_resource(server_dir)
    except Exception:
        pass

    _update_happiness_info(happiness_version, happiness_zip_url)
    _set_status(progress=end_pct)
    _log('HappinessMP update finished')


def _terminate_process(pid: int):
    if not pid:
        return
    try:
        import psutil
        proc = psutil.Process(pid)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        return
    except Exception:
        pass
    if IS_WINDOWS:
        try:
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True, timeout=10)
        except Exception:
            pass
    else:
        try:
            import signal
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass


def _restart_panel(job: dict):
    restart_mode = job.get('restart_mode') or 'standalone'
    server_pid = job.get('server_manager_pid')
    panel_port = _resolve_panel_port(job)
    if restart_mode == 'main':
        restart_flag = DATA_DIR / 'restart.flag'
        restart_flag.write_text('restart', encoding='utf-8')
        _log('Restart flag created, stopping server manager...')
        _terminate_process(server_pid)
        return

    _log('Starting panel process...')
    cwd = str(ROOT_DIR)
    if (ROOT_DIR / 'main.py').exists():
        cmd = [sys.executable, 'main.py', '--port', str(panel_port)]
    else:
        cmd = [sys.executable, 'server_manager.py', '--port', str(panel_port)]
    try:
        popen_kwargs = {'cwd': cwd, 'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}
        if IS_WINDOWS:
            popen_kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
        subprocess.Popen(cmd, **popen_kwargs)
    except Exception:
        pass
    _terminate_process(server_pid)


def _update_connector_config(server_dir, panel_secret, panel_host):
    cfg_path = server_dir / 'hpm-connector.json'
    if not cfg_path.exists():
        _log('No existing hpm-connector.json, creating default...')
        cfg = {}
    else:
        try:
            cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
        except Exception:
            cfg = {}

    cfg.setdefault('api_url', f'http://{panel_host}/connector')
    cfg['api_url'] = f'http://{panel_host}/connector'
    cfg.setdefault('api_secret', panel_secret)
    cfg['api_secret'] = panel_secret
    cfg.setdefault('heartbeat_interval', 30)

    cfg_path.write_text(json.dumps(cfg, indent=4), encoding='utf-8')
    _log('Connector config updated')


def _ensure_connector_resource(server_dir):
    resources_cfg = server_dir / 'resources.xml'
    if not resources_cfg.exists():
        _log('No resources.xml found, creating default...')
        resources_cfg.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<resources>\n'
            '    <resource src="hpm-connector.dll" />\n'
            '</resources>\n',
            encoding='utf-8'
        )
        _log('Created resources.xml with hpm-connector')
        return

    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(str(resources_cfg))
        root = tree.getroot()
        connector_name = 'hpm-connector.dll' if IS_WINDOWS else 'hpm-connector.so'
        found = any(
            res.get('src', '').strip() == connector_name
            for res in root.findall('resource')
        )
        if not found:
            _log('Adding hpm-connector to resources.xml...')
            res_elem = ET.SubElement(root, 'resource')
            res_elem.set('src', connector_name)
            tree.write(str(resources_cfg), encoding='utf-8', xml_declaration=True)
    except Exception as e:
        _log(f'Warning: could not update resources.xml: {e}')


def _get_panel_host():
    panel_cfg = _load_panel_config()
    return panel_cfg.get('panel_host', '127.0.0.1:20000')


def _update_panel(job: dict):
    _log('Starting panel update...')
    _set_status(step='Panel', progress=2)

    panel_info = job.get('panel_info', {})
    panel_version = panel_info.get('version', '')
    panel_zip_url = panel_info.get('zip_url', '')

    if not panel_zip_url:
        raise RuntimeError('No panel zip_url in update job')

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        zip_path = tmpdir / 'panel_update.zip'
        _set_status(step='Panel', progress=3)
        _download_with_progress(panel_zip_url, zip_path, 3, 40, 'Panel files')

        extract_dir = tmpdir / 'panel_extract'
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)

        repo_root = _find_file(extract_dir, 'requirements.txt')
        if repo_root:
            src_root = repo_root.parent
        else:
            src_root = extract_dir

        _set_status(step='Panel', progress=45)
        exclude = {'data', 'HPNMP', 'panel_config.json', '__pycache__', '.git', '.venv', 'venv'}
        for item in src_root.iterdir():
            if item.name in exclude:
                continue
            dest = ROOT_DIR / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=True)
                shutil.copytree(item, dest)
            else:
                if dest.exists():
                    dest.unlink()
                shutil.copy2(item, dest)

    _update_panel_version(panel_version)
    _set_status(step='Panel', progress=80)
    _log('Panel update finished')


def _update_panel_version(version):
    p = ROOT_DIR / 'panel_version.json'
    try:
        p.write_text(json.dumps({'version': version}, indent=4), encoding='utf-8')
    except Exception:
        pass


def run_update(job: dict):
    _status['running'] = True
    _status['finished'] = False
    _status['success'] = False
    _status['error'] = ''
    _status['log'] = []
    _set_status(progress=0, step='Starting', message='Update started')

    try:
        targets = job.get('targets', [])
        for t in targets:
            if t == 'happiness':
                _update_happiness(job)
            elif t == 'panel':
                _update_panel(job)

        _status['running'] = False
        _status['finished'] = True
        _status['success'] = True
        _set_status(progress=100, step='Done', message='Update completed')
        _log('Update completed successfully')

        if job.get('restart', True):
            _log('Restarting panel...')
            _restart_panel(job)

    except Exception as e:
        _status['running'] = False
        _status['finished'] = True
        _status['success'] = False
        _status['error'] = str(e)
        _set_status(progress=0, step='Failed', message=str(e))
        _log(f'Update failed: {e}')


def main():
    parser = argparse.ArgumentParser(description='HMP Panel Updater')
    parser.add_argument('--job', required=True, help='Path to update job JSON')
    args = parser.parse_args()

    try:
        job = json.loads(Path(args.job).read_text(encoding='utf-8'))
    except Exception as e:
        _log(f'Failed to load job file: {e}')
        sys.exit(1)

    run_update(job)


if __name__ == '__main__':
    main()
