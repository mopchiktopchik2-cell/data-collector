import asyncio
import logging
import sqlite3
import threading
from pathlib import Path

from messaging.message import Message


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()
        self._log = logging.getLogger("DATABASE")

    async def connect(self) -> None:
        await asyncio.to_thread(self._connect_sync)

    def _connect_sync(self) -> None:
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS measurements (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id    TEXT NOT NULL,
                device_type  TEXT NOT NULL,
                timestamp    TEXT NOT NULL,
                value        REAL NOT NULL,
                unit         TEXT NOT NULL,
                processed_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()
        self._log.info("[DATABASE] Connected: %s", self.path)

    async def save(self, message: Message) -> None:
        await asyncio.to_thread(self._save_sync, message)

    def _save_sync(self, message: Message) -> None:
        with self._lock:
            if self._conn is None:
                raise RuntimeError("Database is not connected")
            try:
                self._conn.execute(
                    "INSERT INTO measurements "
                    "(device_id, device_type, timestamp, value, unit, processed_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        message.device_id,
                        message.device_type,
                        message.timestamp,
                        message.value,
                        message.unit,
                        message.processed_at,
                    ),
                )
                self._conn.commit()
            except sqlite3.Error:
                self._log.exception("[DATABASE] Failed to save measurement")
                raise
        self._log.info("[DATABASE] Measurement saved")

    async def close(self) -> None:
        await asyncio.to_thread(self._close_sync)

    def _close_sync(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None
                self._log.info("[DATABASE] Closed")