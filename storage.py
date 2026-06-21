import json
import os
from pathlib import Path

import db

DATA_DIR = Path('./data')
USERS_FILE = DATA_DIR / 'users.json'
CONFIG_FILE = DATA_DIR / 'config.json'
PANEL_CONFIG_FILE = Path('./panel_config.json')
BANS_FILE = DATA_DIR / 'bans.json'
PLAYER_PROFILES_FILE = DATA_DIR / 'player_profiles.json'

DATA_DIR.mkdir(exist_ok=True)

IS_WINDOWS = (os.name == 'nt')
SERVER_BINARY = 'HappMP.exe' if IS_WINDOWS else 'HappMP'


def _default_status_embed_template():
    return {
        "title": "{{serverName}}",
        "description": "",
        "fields": [
            {
                "name": "> STATUS",
                "value": "```\n{{statusString}}\n```",
                "inline": True
            },
            {
                "name": "> PLAYERS",
                "value": "```\n{{serverClients}}/{{serverMaxClients}}\n```",
                "inline": True
            },
            {
                "name": "> F8 CONNECT COMMAND",
                "value": "```\nconnect play.xanite.cz\n```"
            },
            {
                "name": "> NEXT RESTART",
                "value": "```\n{{nextScheduledRestart}}\n```",
                "inline": True
            },
            {
                "name": "> UPTIME",
                "value": "```\n{{uptime}}\n```",
                "inline": True
            }
        ],
        "image": {},
        "thumbnail": {}
    }


def _default_status_config():
    return {
        "onlineString": " Online",
        "onlineColor": "#0BA70B",
        "partialString": " Partial",
        "partialColor": "#FFF100",
        "offlineString": " Offline",
        "offlineColor": "#A70B28",
        "buttons": []
    }


def _default_discord_settings():
    return {
        'enabled': False,
        'token': '',
        'guild_id': '',
        'warnings_channel_id': '',
        'status_embed_json': json.dumps(_default_status_embed_template(), indent=4, ensure_ascii=False),
        'status_config_json': json.dumps(_default_status_config(), indent=4, ensure_ascii=False),
        'status_messages': []
    }


def _normalize_discord_settings(data):
    base = _default_discord_settings()
    incoming = data if isinstance(data, dict) else {}

    base['enabled'] = bool(incoming.get('enabled', base['enabled']))
    base['token'] = str(incoming.get('token', base['token']) or '').strip()
    base['guild_id'] = str(incoming.get('guild_id', base['guild_id']) or '').strip()
    base['warnings_channel_id'] = str(incoming.get('warnings_channel_id', base['warnings_channel_id']) or '').strip()

    status_embed_json = incoming.get('status_embed_json')
    if isinstance(status_embed_json, str) and status_embed_json.strip():
        base['status_embed_json'] = status_embed_json

    status_config_json = incoming.get('status_config_json')
    if isinstance(status_config_json, str) and status_config_json.strip():
        base['status_config_json'] = status_config_json

    status_messages = incoming.get('status_messages')
    if isinstance(status_messages, list):
        cleaned = []
        for item in status_messages:
            if not isinstance(item, dict):
                continue
            channel_id = str(item.get('channel_id') or '').strip()
            message_id = str(item.get('message_id') or '').strip()
            if not channel_id or not message_id:
                continue
            cleaned.append({
                'channel_id': channel_id,
                'message_id': message_id
            })
        base['status_messages'] = cleaned

    return base


def _default_panel_config():
    return {
        'locale': 'en',
        'panel_name': 'HappinessMP',
        'auto_start': False,
        'scheduled_restarts': [],
        'panel_secret': 'changeme',
        'panel_version': '0.0.0',
        'panel_port': 20000,
        'discord': _default_discord_settings()
    }


def _json_load(path: Path, default):
    try:
        if path.exists():
            with open(path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _json_save(path: Path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def db_enabled():
    return db.is_configured()


def _db_get_app_config(name: str):
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT json FROM app_config WHERE name=%s', (name,))
            row = cur.fetchone()
            if not row:
                return None
            return json.loads(row['json'])
    finally:
        conn.close()


def _db_set_app_config(name: str, data: dict):
    payload = json.dumps(data, ensure_ascii=True)
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO app_config (name, json) VALUES (%s, %s) '
                'ON DUPLICATE KEY UPDATE json=VALUES(json)',
                (name, payload)
            )
    finally:
        conn.close()


def _db_users_count():
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) AS cnt FROM users')
            row = cur.fetchone()
            return int(row['cnt'] or 0)
    finally:
        conn.close()


def _db_load_users():
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT username, password_hash, role, force_password_change, '
                'created_at, last_login, enabled, permissions_json, '
                'display_name, avatar '
                'FROM users'
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    users = {}
    for row in rows:
        perms = {}
        if row.get('permissions_json'):
            try:
                perms = json.loads(row['permissions_json'])
            except Exception:
                perms = {}
        users[row['username']] = {
            'password': row['password_hash'],
            'role': row.get('role') or 'user',
            'force_password_change': bool(row.get('force_password_change')),
            'created_at': row.get('created_at'),
            'last_login': row.get('last_login'),
            'enabled': bool(row.get('enabled', 1)),
            'permissions': perms,
            'display_name': row.get('display_name') or '',
            'avatar': row.get('avatar') or ''
        }
    return users


def _db_save_users(users: dict):
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT username FROM users')
            existing = {row['username'] for row in cur.fetchall()}

            new_users = set(users.keys())
            to_delete = existing - new_users
            if to_delete:
                placeholders = ','.join(['%s'] * len(to_delete))
                cur.execute(
                    f'DELETE FROM users WHERE username IN ({placeholders})',
                    tuple(to_delete)
                )

            for username, u in users.items():
                perms_json = json.dumps(u.get('permissions', {}), ensure_ascii=True)
                cur.execute(
                    'INSERT INTO users '
                    '(username, password_hash, role, force_password_change, created_at, last_login, '
                    'enabled, permissions_json, display_name, avatar) '
                    'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
                    'ON DUPLICATE KEY UPDATE '
                    'password_hash=VALUES(password_hash), '
                    'role=VALUES(role), '
                    'force_password_change=VALUES(force_password_change), '
                    'created_at=VALUES(created_at), '
                    'last_login=VALUES(last_login), '
                    'enabled=VALUES(enabled), '
                    'permissions_json=VALUES(permissions_json), '
                    'display_name=VALUES(display_name), '
                    'avatar=VALUES(avatar)',
                    (
                        username,
                        u.get('password'),
                        u.get('role', 'user'),
                        1 if u.get('force_password_change') else 0,
                        u.get('created_at'),
                        u.get('last_login'),
                        1 if u.get('enabled', True) else 0,
                        perms_json,
                        u.get('display_name'),
                        u.get('avatar')
                    )
                )
    finally:
        conn.close()


def load_users():
    if db_enabled():
        try:
            return _db_load_users()
        except Exception:
            pass
    return _json_load(USERS_FILE, {})


def save_users(users: dict):
    if db_enabled():
        _db_save_users(users)
        return
    _json_save(USERS_FILE, users)


def load_config():
    default_config = {
        'server_path': f'./HPNMP/{SERVER_BINARY}',
        'server_name': SERVER_BINARY,
        'log_file': './HPNMP/server.log',
        'auto_restart': False,
        'restart_delay': 5,
        'max_restarts': 10,
        'happiness_version': '0.0.0',
        'happiness_zip_url': ''
    }
    if db_enabled():
        data = _db_get_app_config('server')
        if data is None:
            _db_set_app_config('server', default_config)
            return dict(default_config)
        for k, v in default_config.items():
            data.setdefault(k, v)
        return data

    data = _json_load(CONFIG_FILE, None)
    if data is None:
        _json_save(CONFIG_FILE, default_config)
        return dict(default_config)
    for k, v in default_config.items():
        data.setdefault(k, v)
    return data


def save_config(cfg: dict):
    if db_enabled():
        _db_set_app_config('server', cfg)
        return
    _json_save(CONFIG_FILE, cfg)


def load_panel_config():
    defaults = _default_panel_config()
    if db_enabled():
        data = _db_get_app_config('panel')
        if data is None:
            _db_set_app_config('panel', defaults)
            return dict(defaults)
        for k, v in defaults.items():
            if k == 'discord':
                data['discord'] = _normalize_discord_settings(data.get('discord'))
            else:
                data.setdefault(k, v)
        return data

    data = _json_load(PANEL_CONFIG_FILE, None)
    if data is None:
        _json_save(PANEL_CONFIG_FILE, defaults)
        return dict(defaults)
    for k, v in defaults.items():
        if k == 'discord':
            data['discord'] = _normalize_discord_settings(data.get('discord'))
        else:
            data.setdefault(k, v)
    return data


def save_panel_config(cfg: dict):
    if db_enabled():
        _db_set_app_config('panel', cfg)
        return
    _json_save(PANEL_CONFIG_FILE, cfg)


def load_bans():
    if db_enabled():
        conn = db.connect()
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT ip, name, reason, banned_by, banned_at FROM bans ORDER BY id')
                rows = cur.fetchall()
        finally:
            conn.close()
        return list(rows)
    return _json_load(BANS_FILE, [])


def save_bans(bans: list):
    if db_enabled():
        conn = db.connect()
        try:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM bans')
                for b in bans:
                    cur.execute(
                        'INSERT INTO bans (ip, name, reason, banned_by, banned_at) '
                        'VALUES (%s,%s,%s,%s,%s)',
                        (
                            b.get('ip'),
                            b.get('name'),
                            b.get('reason'),
                            b.get('banned_by'),
                            b.get('banned_at')
                        )
                    )
        finally:
            conn.close()
        return
    _json_save(BANS_FILE, bans)


def load_player_profiles():
    if db_enabled():
        data = _db_get_app_config('player_profiles')
        if isinstance(data, dict):
            profiles = data.get('profiles', data)
            if isinstance(profiles, dict):
                return profiles
        return {}
    data = _json_load(PLAYER_PROFILES_FILE, {})
    if isinstance(data, dict):
        return data
    return {}


def save_player_profiles(profiles: dict):
    if not isinstance(profiles, dict):
        profiles = {}
    if db_enabled():
        _db_set_app_config('player_profiles', {'profiles': profiles})
        return
    _json_save(PLAYER_PROFILES_FILE, profiles)


def migrate_json_to_db(force: bool = False):
    if not db_enabled():
        return
    db.ensure_schema()

    if USERS_FILE.exists():
        users = _json_load(USERS_FILE, {})
        if users:
            if force or _db_users_count() == 0:
                _db_save_users(users)

    if CONFIG_FILE.exists():
        cfg = _json_load(CONFIG_FILE, None)
        if cfg is not None:
            if force or _db_get_app_config('server') is None:
                _db_set_app_config('server', cfg)

    if PANEL_CONFIG_FILE.exists():
        cfg = _json_load(PANEL_CONFIG_FILE, None)
        if cfg is not None:
            if force or _db_get_app_config('panel') is None:
                _db_set_app_config('panel', cfg)

    if BANS_FILE.exists():
        bans = _json_load(BANS_FILE, [])
        if bans:
            conn = db.connect()
            try:
                with conn.cursor() as cur:
                    if force:
                        cur.execute('DELETE FROM bans')
                    else:
                        cur.execute('SELECT COUNT(*) AS cnt FROM bans')
                        row = cur.fetchone()
                        if row and int(row['cnt'] or 0) > 0:
                            return
                        cur.execute('DELETE FROM bans')
                    for b in bans:
                        cur.execute(
                            'INSERT INTO bans (ip, name, reason, banned_by, banned_at) '
                            'VALUES (%s,%s,%s,%s,%s)',
                            (
                                b.get('ip'),
                                b.get('name'),
                                b.get('reason'),
                                b.get('banned_by'),
                                b.get('banned_at')
                            )
                        )
            finally:
                conn.close()

    if PLAYER_PROFILES_FILE.exists():
        profiles = _json_load(PLAYER_PROFILES_FILE, {})
        if isinstance(profiles, dict):
            if force or _db_get_app_config('player_profiles') is None:
                _db_set_app_config('player_profiles', {'profiles': profiles})
