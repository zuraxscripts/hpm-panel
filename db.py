import json
import os
from pathlib import Path

import pymysql

try:
    from cryptography.fernet import Fernet
except Exception:                                                
    Fernet = None

DATA_DIR = Path('./data')
DB_CONFIG_FILE = DATA_DIR / 'db.json'
DB_KEY_FILE = DATA_DIR / 'db.key'

DATA_DIR.mkdir(exist_ok=True)


def _env_config():
    host = os.getenv('HAPPINESS_DB_HOST')
    port = os.getenv('HAPPINESS_DB_PORT')
    user = os.getenv('HAPPINESS_DB_USER')
    password = os.getenv('HAPPINESS_DB_PASSWORD')
    database = os.getenv('HAPPINESS_DB_NAME')
    if not host or not user or not password or not database:
        return None
    return {
        'host': host,
        'port': int(port) if port else 3306,
        'user': user,
        'password': password,
        'database': database,
        'source': 'env'
    }


def is_configured():
    if _env_config():
        return True
    return DB_CONFIG_FILE.exists()


def _get_fernet():
    if Fernet is None:
        raise RuntimeError('cryptography is required for encrypted DB credentials')
    if DB_KEY_FILE.exists():
        key = DB_KEY_FILE.read_bytes().strip()
    else:
        key = Fernet.generate_key()
        DB_KEY_FILE.write_bytes(key)
        try:
            os.chmod(DB_KEY_FILE, 0o600)
        except Exception:
            pass
    return Fernet(key)


def encrypt_secret(value: str) -> str:
    f = _get_fernet()
    return f.encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt_secret(value: str) -> str:
    f = _get_fernet()
    return f.decrypt(value.encode('utf-8')).decode('utf-8')


def save_db_config(cfg: dict):
    host = (cfg.get('host') or '').strip()
    user = (cfg.get('user') or '').strip()
    password = cfg.get('password') or ''
    database = (cfg.get('database') or '').strip()
    port = cfg.get('port')
    if not host or not user or not password or not database:
        raise ValueError('DB config requires host, user, password, database')
    try:
        port = int(port) if port else 3306
    except Exception:
        port = 3306

    payload = {
        'host': host,
        'port': port,
        'user': user,
        'password_enc': encrypt_secret(password),
        'database': database
    }
    DB_CONFIG_FILE.write_text(json.dumps(payload, indent=4), encoding='utf-8')
    try:
        os.chmod(DB_CONFIG_FILE, 0o600)
    except Exception:
        pass


def load_db_config():
    env = _env_config()
    if env:
        return env
    if not DB_CONFIG_FILE.exists():
        return None
    data = json.loads(DB_CONFIG_FILE.read_text(encoding='utf-8'))
    password = data.get('password')
    if not password:
        enc = data.get('password_enc')
        if enc:
            password = decrypt_secret(enc)
    if not password:
        raise RuntimeError('DB password missing (no password or password_enc)')
    return {
        'host': data.get('host'),
        'port': int(data.get('port') or 3306),
        'user': data.get('user'),
        'password': password,
        'database': data.get('database'),
        'source': 'file'
    }


def connect():
    cfg = load_db_config()
    if not cfg:
        raise RuntimeError('DB config not set')
    return pymysql.connect(
        host=cfg['host'],
        port=cfg.get('port', 3306),
        user=cfg['user'],
        password=cfg['password'],
        database=cfg['database'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def test_connection(cfg: dict):
    conn = pymysql.connect(
        host=cfg.get('host'),
        port=int(cfg.get('port') or 3306),
        user=cfg.get('user'),
        password=cfg.get('password'),
        database=cfg.get('database'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=5
    )
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
    finally:
        conn.close()


def ensure_schema():
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS app_config (
                    name VARCHAR(64) PRIMARY KEY,
                    json TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(64) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(32) NOT NULL,
                    force_password_change TINYINT(1) NOT NULL DEFAULT 0,
                    created_at VARCHAR(64),
                    last_login VARCHAR(64),
                    enabled TINYINT(1) NOT NULL DEFAULT 1,
                    permissions_json TEXT,
                    display_name VARCHAR(64),
                    avatar MEDIUMTEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS bans (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ip VARCHAR(64),
                    name VARCHAR(128),
                    reason TEXT,
                    banned_by VARCHAR(64),
                    banned_at VARCHAR(64)
                )
                """
            )
                                                     
            cur.execute("SHOW COLUMNS FROM users LIKE 'display_name'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE users ADD COLUMN display_name VARCHAR(64)")
            cur.execute("SHOW COLUMNS FROM users LIKE 'avatar'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE users ADD COLUMN avatar MEDIUMTEXT")
            cur.execute("SHOW COLUMNS FROM users LIKE 'password_hash'")
            row = cur.fetchone()
            if row:
                col_type = str(row.get('Type') or '').lower().strip()
                if col_type.startswith('varchar(') and col_type.endswith(')'):
                    try:
                        size = int(col_type[len('varchar('):-1])
                    except Exception:
                        size = 255
                    if size < 255:
                        cur.execute("ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255) NOT NULL")
    finally:
        conn.close()
