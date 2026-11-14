
import os
import sqlite3
import hashlib
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env", override=True)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SQLITE_DATABASE = PROJECT_DIR / "data" / "remote_activity.db"


def get_postgres_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")
    return psycopg2.connect(DATABASE_URL)


def initialize_database():
    if DATABASE_URL:
        with get_postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activity (
                        id BIGSERIAL PRIMARY KEY,
                        device_name VARCHAR(100) NOT NULL,
                        action VARCHAR(30) NOT NULL,
                        item_type VARCHAR(20) NOT NULL,
                        path VARCHAR(2000) NOT NULL,
                        timestamp VARCHAR(40) NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS devices (
                        device_id VARCHAR(100) PRIMARY KEY,
                        device_name VARCHAR(100) NOT NULL,
                        token_hash VARCHAR(64) NOT NULL,
                        active BOOLEAN NOT NULL DEFAULT TRUE,
                        created_at VARCHAR(40) NOT NULL
                    )
                """)
    else:
        SQLITE_DATABASE.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(SQLITE_DATABASE) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    device_name TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def register_device(device_id, device_name, token, timestamp):
    token_hash = hash_token(token)

    if DATABASE_URL:
        with get_postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO devices
                    (device_id, device_name, token_hash, active, created_at)
                    VALUES (%s, %s, %s, TRUE, %s)
                """, (device_id, device_name, token_hash, timestamp))
    else:
        with sqlite3.connect(SQLITE_DATABASE) as connection:
            connection.execute("""
                INSERT INTO devices
                (device_id, device_name, token_hash, active, created_at)
                VALUES (?, ?, ?, 1, ?)
            """, (device_id, device_name, token_hash, timestamp))


def authenticate_device(token):
    token_hash = hash_token(token)

    if DATABASE_URL:
        with get_postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT device_id, device_name
                    FROM devices
                    WHERE token_hash = %s AND active = TRUE
                """, (token_hash,))
                return cursor.fetchone()
    else:
        with sqlite3.connect(SQLITE_DATABASE) as connection:
            return connection.execute("""
                SELECT device_id, device_name
                FROM devices
                WHERE token_hash = ? AND active = 1
            """, (token_hash,)).fetchone()


def revoke_device(device_id):
    if DATABASE_URL:
        with get_postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE devices
                    SET active = FALSE
                    WHERE device_id = %s
                """, (device_id,))
                return cursor.rowcount > 0
    else:
        with sqlite3.connect(SQLITE_DATABASE) as connection:
            cursor = connection.execute("""
                UPDATE devices
                SET active = 0
                WHERE device_id = ?
            """, (device_id,))
            return cursor.rowcount > 0


def insert_activity(device_name, action, item_type, path, timestamp):
    values = (device_name, action, item_type, path, timestamp)

    if DATABASE_URL:
        with get_postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO activity
                    (device_name, action, item_type, path, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, values)
    else:
        with sqlite3.connect(SQLITE_DATABASE) as connection:
            connection.execute("""
                INSERT INTO activity
                (device_name, action, item_type, path, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, values)
def get_recent_activity(limit=100):
    limit = max(1, min(int(limit), 500))

    if DATABASE_URL:
        with get_postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT device_name, action, item_type, path, timestamp
                    FROM activity
                    ORDER BY id DESC
                    LIMIT %s
                """, (limit,))
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_DATABASE) as connection:
            rows = connection.execute("""
                SELECT device_name, action, item_type, path, timestamp
                FROM activity
                ORDER BY id DESC
                LIMIT ?
            """, (limit,)).fetchall()

    return [
        {
            "device_name": row[0],
            "action": row[1],
            "item_type": row[2],
            "path": row[3],
            "timestamp": row[4],
        }
        for row in rows
    ]


def get_devices():
    if DATABASE_URL:
        with get_postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT device_id, device_name, active, created_at
                    FROM devices
                    ORDER BY created_at DESC
                """)
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_DATABASE) as connection:
            rows = connection.execute("""
                SELECT device_id, device_name, active, created_at
                FROM devices
                ORDER BY created_at DESC
            """).fetchall()

    return [
        {
            "device_id": row[0],
            "device_name": row[1],
            "active": bool(row[2]),
            "created_at": row[3],
        }
        for row in rows
    ]