"""
Updater for HappinessMP Panel + Server files.
"""

import argparse
import json
import os
import shutil
import subprocess
import stat
import sys
import tempfile
import time
import urllib.request
import zipfile
import signal
import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
USER_AGENT = 'HPM-Panel-Updater/1.0'
DATA_DIR = ROOT_DIR / 'data'
STATUS_FILE = DATA_DIR / 'update_status.json'
LOG_FILE = DATA_DIR / 'update.log'
PANEL_DEFAULT_HOST = 'http://127.0.0.1:20000'
CONNECTOR_API_URL = 'https://api.github.com/repos/zuraxscripts/hpm-connector/releases/latest'


DATA_DIR.mkdir(exist_ok=True)


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


def _json_load(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8-sig'))
    except Exception:
        pass
    return default


def _json_save(path: Path, payload: dict):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, indent=4), encoding='utf-8')
    os.replace(tmp, path)


def _log(message: str):
    timestamp = time.strftime('%H:%M:%S')
    line = f'[{timestamp}] {message}'
    _status['message'] = message
    _status['log'].append(line)
    if len(_status['log']) > 200:
        _status['log'] = _status['log'][-200:]
    _status['updated_at'] = time.time()
    _json_save(STATUS_FILE, _status)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def _set_status(**kwargs):
    _status.update(kwargs)
    _status['updated_at'] = time.time()
    _json_save(STATUS_FILE, _status)


def _download_with_progress(url: str, dest_path: Path, start_pct: int, end_pct: int, label: str):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req) as resp, open(dest_path, 'wb') as f:
        total = resp.getheader('Content-Length')
        try:
            total = int(total) if total else None
        except Exception:
            total = None

        downloaded = 0
        last_tick = time.time()
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = start_pct + (downloaded / total) * (end_pct - start_pct)
            else:
                pct = min(end_pct, start_pct + 1)
            if time.time() - last_tick > 0.5:
                _set_status(progress=int(pct))
                _log(f'{label}: {downloaded / (1024 * 1024):.1f} MB')
                last_tick = time.time()
        _set_status(progress=end_pct)
        _log(f'{label}: download complete')


def _find_file(root: Path, filename: str):
    for p in root.rglob(filename):
        return p
    return None


def _should_skip(rel_path: Path, skip_top: set, skip_files: set, skip_any: set):
    parts = rel_path.parts
    if not parts:
        return False
    if any(p in skip_any for p in parts):
        return True
    if parts[0] in skip_top:
        return True
    if len(parts) == 1 and parts[0] in skip_files:
        return True
    return False


def _copy_tree(src_root: Path, dst_root: Path, skip_top: set, skip_files: set, skip_any: set):
    for item in src_root.rglob('*'):
        rel = item.relative_to(src_root)
        if _should_skip(rel, skip_top, skip_files, skip_any):
            continue
        dest = dst_root / rel
        if item.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)


def _merge_resources(src_res: Path, dst_res: Path, replace_names: set):
    dst_res.mkdir(parents=True, exist_ok=True)
    for item in src_res.iterdir():
        target = dst_res / item.name
        if item.name in replace_names:
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
        else:
            if target.exists():
                continue
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)


def _merge_server_tree(src_root: Path, dst_root: Path):
    for item in src_root.iterdir():
        dest = dst_root / item.name
        if item.name == 'resources' and item.is_dir():
            _merge_resources(item, dest, {'lua-gamemode', 'squirrel-gamemode'})
            continue
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)


def _load_panel_config():
    try:
        sys.path.insert(0, str(ROOT_DIR))
        import storage                                
        return storage.load_panel_config()
    except Exception:
        return {}


def _load_server_config():
    try:
        sys.path.insert(0, str(ROOT_DIR))
        import storage                                
        return storage.load_config()
    except Exception:
        return {}


def _save_panel_config(cfg: dict):
    try:
        sys.path.insert(0, str(ROOT_DIR))
        import storage                                
        storage.save_panel_config(cfg)
    except Exception:
        pass


def _save_server_config(cfg: dict):
    try:
        sys.path.insert(0, str(ROOT_DIR))
        import storage                                
        storage.save_config(cfg)
    except Exception:
        pass


def _parse_settings_xml(path: Path):
    try:
        import xml.etree.ElementTree as ET
        if not path.exists():
            return None
        tree = ET.parse(path)
        root = tree.getroot()
        data = {}
        resources = []
        for child in root:
            tag = child.tag
            if tag == 'resource':
                if child.text:
                    resources.append(child.text.strip())
            else:
                data[tag] = child.text if child.text is not None else ''
        data['resources'] = resources
        return data
    except Exception:
        return None


def _write_settings_xml(path: Path, data: dict):
    import xml.etree.ElementTree as ET
    root = ET.Element('settings')
    simple_fields = ['hostname', 'hostaddress', 'listed', 'port', 'maxplayers',
                     'episode', 'secret', 'loglevel', 'chat']
    for field in simple_fields:
        if field in data:
            el = ET.SubElement(root, field)
            val = data[field]
            if isinstance(val, bool):
                el.text = 'true' if val else 'false'
            else:
                el.text = str(val)
    for res in data.get('resources', []):
        el = ET.SubElement(root, 'resource')
        el.text = str(res).strip()
    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(path, encoding='unicode', xml_declaration=True)


def _install_connector(server_dir: Path):
    _log('Resolving latest hpm-connector release...')
    req = urllib.request.Request(CONNECTOR_API_URL, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    zip_url = data.get('zipball_url')
    tag = data.get('tag_name') or 'latest'
    if not zip_url:
        raise RuntimeError('Failed to resolve hpm-connector release zipball')

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        zip_path = tmpdir / f'hpm_connector_{tag}.zip'
        _download_with_progress(zip_url, zip_path, _status['progress'], min(95, _status['progress'] + 10), f'hpm-connector {tag}')

        extract_dir = tmpdir / 'connector_extract'
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)

        top_dirs = [p for p in extract_dir.iterdir() if p.is_dir()]
        source_dir = top_dirs[0] if top_dirs else extract_dir

        resources_dir = server_dir / 'resources'
        target_dir = resources_dir / 'hpm-connector'
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)

    _log('hpm-connector installed')


def _update_connector_config(server_dir: Path, panel_secret: str, panel_host: str = None):
    panel_host = panel_host or PANEL_DEFAULT_HOST
    server_lua = server_dir / 'resources' / 'hpm-connector' / 'server.lua'
    if not server_lua.exists():
        raise RuntimeError('hpm-connector server.lua not found')
    text = server_lua.read_text(encoding='utf-8', errors='ignore')
    text, host_count = re.subn(
        r'(?m)^local\s+PANEL_HOST\s*=.*$',
        f'local PANEL_HOST = "{panel_host}"',
        text
    )
    text, secret_count = re.subn(
        r'(?m)^local\s+PANEL_SECRET\s*=.*$',
        f'local PANEL_SECRET = "{panel_secret}"',
        text
    )
    if host_count == 0:
        text = f'local PANEL_HOST = "{panel_host}"\n' + text
    if secret_count == 0:
        text = f'local PANEL_SECRET = "{panel_secret}"\n' + text
    server_lua.write_text(text, encoding='utf-8')


def _ensure_connector_resource(server_dir: Path):
    settings_path = server_dir / 'settings.xml'
    data = _parse_settings_xml(settings_path) or {}
    resources = data.get('resources', [])
    if 'hpm-connector' not in resources:
        resources.append('hpm-connector')
        data['resources'] = resources
        _write_settings_xml(settings_path, data)
        _log('settings.xml updated with hpm-connector')


def _update_panel_version(version: str):
    if not version:
        return
    cfg = _load_panel_config()
    cfg['panel_version'] = str(version)
    _save_panel_config(cfg)


def _update_happiness_info(version: str, zip_url: str):
    if not version:
        return
    cfg = _load_server_config()
    cfg['happiness_version'] = str(version)
    if zip_url:
        cfg['happiness_zip_url'] = str(zip_url)
    _save_server_config(cfg)


def perform_panel_update(panel_zip_url: str, panel_version: str, start_pct: int, end_pct: int):
    _log('Starting panel update')
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        zip_path = tmpdir / 'panel.zip'
        span = max(1, end_pct - start_pct)
        dl_end = start_pct + int(span * 0.6)
        extract_end = start_pct + int(span * 0.8)
        _set_status(step='Panel', progress=start_pct)
        _download_with_progress(panel_zip_url, zip_path, start_pct, dl_end, 'Panel files')

        extract_dir = tmpdir / 'panel_extract'
        extract_dir.mkdir(parents=True, exist_ok=True)
        _log('Extracting panel files...')
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)
        _set_status(progress=extract_end)

        top_dirs = [p for p in extract_dir.iterdir() if p.is_dir()]
        source_dir = top_dirs[0] if top_dirs else extract_dir

        skip_top = {'data', 'HPNMP'}
        skip_files = {'panel_config.json', 'server_config.json', 'panel_version.json', 'happiness_update.json', 'update_config.json'}
        skip_any = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}

        _log('Copying panel files...')
        _copy_tree(source_dir, ROOT_DIR, skip_top, skip_files, skip_any)

    _update_panel_version(panel_version)
    _set_status(progress=end_pct)
    _log('Panel update finished')


def perform_happiness_update(happiness_zip_url: str, happiness_version: str, start_pct: int, end_pct: int):
    _log('Starting HappinessMP update')
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        zip_path = tmpdir / 'happiness.zip'
        span = max(1, end_pct - start_pct)
        dl_end = start_pct + int(span * 0.6)
        extract_end = start_pct + int(span * 0.75)
        _set_status(step='HappinessMP', progress=start_pct)
        _download_with_progress(happiness_zip_url, zip_path, start_pct, dl_end, 'HappinessMP files')

        extract_dir = tmpdir / 'server_extract'
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)
        _set_status(progress=extract_end)

        server_bin = _find_file(extract_dir, 'HappinessMP.Server.out')
        if not server_bin:
            raise RuntimeError('HappinessMP.Server.out not found in extracted server files')

        server_root = server_bin.parent
        server_cfg = _load_server_config()
        server_path = server_cfg.get('server_path', './HPNMP/HappMP')
        server_dir = Path(server_path).resolve().parent
        if not server_dir.exists():
            raise RuntimeError(f'Server directory not found: {server_dir}')

        _log('Updating server files...')
        _merge_server_tree(server_root, server_dir)

        src = server_dir / 'HappinessMP.Server.out'
        dst = server_dir / 'HappMP'
        if src.exists():
            if dst.exists():
                dst.unlink()
            src.rename(dst)
        if dst.exists():
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
            _update_connector_config(server_dir, panel_secret, PANEL_DEFAULT_HOST)
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
    try:
        os.kill(pid, signal.SIGTERM)
    except Exception:
        pass


def _restart_panel(job: dict):
    restart_mode = job.get('restart_mode') or 'standalone'
    server_pid = job.get('server_manager_pid')
    if restart_mode == 'main':
                                                              
        restart_flag = DATA_DIR / 'restart.flag'
        restart_flag.write_text('restart', encoding='utf-8')
        _log('Restart flag created, stopping server manager...')
        _terminate_process(server_pid)
        return

    _log('Starting panel process...')
    cwd = str(ROOT_DIR)
    if (ROOT_DIR / 'main.py').exists():
        cmd = [sys.executable, 'main.py']
    else:
        cmd = [sys.executable, 'server_manager.py']
    try:
        subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    _terminate_process(server_pid)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', required=True)
    args = parser.parse_args()

    job_path = Path(args.job).resolve()
    job = _json_load(job_path, {})
    targets = job.get('targets') or []

    _status.update(STATUS_TEMPLATE)
    _status['running'] = True
    _status['finished'] = False
    _status['success'] = False
    _status['progress'] = 0
    _status['step'] = 'Starting'
    _status['targets'] = targets
    _json_save(STATUS_FILE, _status)
    _log('Updater started')

    try:
        ranges = {}
        if 'panel' in targets and 'happiness' in targets:
            ranges['panel'] = (5, 55)
            ranges['happiness'] = (55, 95)
        elif 'panel' in targets:
            ranges['panel'] = (5, 95)
        elif 'happiness' in targets:
            ranges['happiness'] = (5, 95)

        if 'panel' in targets:
            panel = job.get('panel') or {}
            panel_zip = panel.get('zip_url')
            panel_ver = panel.get('version')
            if not panel_zip:
                raise RuntimeError('Panel update requested but zip_url missing')
            start_pct, end_pct = ranges.get('panel', (5, 95))
            perform_panel_update(panel_zip, panel_ver, start_pct, end_pct)

        if 'happiness' in targets:
            happ = job.get('happiness') or {}
            happ_zip = happ.get('zip_url')
            happ_ver = happ.get('version')
            if not happ_zip:
                raise RuntimeError('Happiness update requested but zip_url missing')
            start_pct, end_pct = ranges.get('happiness', (5, 95))
            perform_happiness_update(happ_zip, happ_ver, start_pct, end_pct)

        _set_status(progress=100, step='Done', finished=True, success=True, running=False)
        _log('Update completed successfully')
    except Exception as e:
        _set_status(finished=True, success=False, running=False, error=str(e))
        _log(f'Update failed: {e}')
        return

                   
    _restart_panel(job)


if __name__ == '__main__':
    main()
