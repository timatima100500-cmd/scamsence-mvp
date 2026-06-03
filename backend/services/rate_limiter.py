"""
backend/services/rate_limiter.py - IP-based Rate Limiter

Free plan: 5 checks per day per IP.
Storage: SQLite (no external dependencies).
Resets at midnight UTC.
"""
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

# SQLite хранится рядом с проектом, не в venv
_DB_PATH = Path(__file__).parent.parent.parent / "data" / "rate_limits.db"
_FREE_LIMIT = 5   # проверок в день для бесплатного плана
_WINDOW_SEC = 86400  # 24 часа в секундах


def _get_conn() -> sqlite3.Connection:
    """Создаёт подключение и таблицу если не существует."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ip_checks (
            ip          TEXT NOT NULL,
            date        TEXT NOT NULL,   -- формат YYYY-MM-DD UTC
            count       INTEGER DEFAULT 0,
            last_check  REAL NOT NULL,   -- unix timestamp
            PRIMARY KEY (ip, date)
        )
    """)
    conn.commit()
    return conn


class RateLimiter:
    """
    IP-based rate limiter.
    Используем одно соединение на весь lifecycle приложения (singleton).
    SQLite thread-safe через check_same_thread=False + WAL mode.
    """

    def __init__(self, daily_limit: int = _FREE_LIMIT) -> None:
        self._limit = daily_limit
        self._conn = _get_conn()
        # WAL mode — лучше для concurrent reads
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.commit()

    def _today_utc(self) -> str:
        """Возвращает сегодняшнюю дату в UTC как строку YYYY-MM-DD."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def check_and_increment(self, ip: str) -> dict:
        """
        Проверяет лимит для IP и инкрементирует счётчик.
        Возвращает: {allowed: bool, count: int, limit: int, remaining: int}

        Логика: если запись на сегодня есть — проверяем count,
        если нет — создаём с count=0 перед инкрементом.
        """
        today = self._today_utc()
        now = time.time()

        with self._conn:
            # Upsert: создаём запись или обновляем существующую
            self._conn.execute("""
                INSERT INTO ip_checks (ip, date, count, last_check)
                VALUES (?, ?, 0, ?)
                ON CONFLICT(ip, date) DO NOTHING
            """, (ip, today, now))

            row = self._conn.execute(
                "SELECT count FROM ip_checks WHERE ip=? AND date=?",
                (ip, today)
            ).fetchone()

            current_count = row[0] if row else 0

            if current_count >= self._limit:
                # Лимит исчерпан — не инкрементируем
                return {
                    "allowed": False,
                    "count": current_count,
                    "limit": self._limit,
                    "remaining": 0,
                    "reset_at": f"{today}T23:59:59Z",
                }

            # Инкрементируем
            new_count = current_count + 1
            self._conn.execute("""
                UPDATE ip_checks SET count=?, last_check=?
                WHERE ip=? AND date=?
            """, (new_count, now, ip, today))

        return {
            "allowed": True,
            "count": new_count,
            "limit": self._limit,
            "remaining": self._limit - new_count,
            "reset_at": f"{today}T23:59:59Z",
        }

    def get_status(self, ip: str) -> dict:
        """Возвращает текущий статус без инкрементирования."""
        today = self._today_utc()
        row = self._conn.execute(
            "SELECT count FROM ip_checks WHERE ip=? AND date=?",
            (ip, today)
        ).fetchone()
        count = row[0] if row else 0
        return {
            "count": count,
            "limit": self._limit,
            "remaining": max(0, self._limit - count),
            "reset_at": f"{today}T23:59:59Z",
        }

    def cleanup_old_records(self, days_to_keep: int = 7) -> int:
        """Удаляет записи старше N дней. Запускать периодически."""
        cutoff = datetime.now(timezone.utc)
        cutoff_str = cutoff.strftime("%Y-%m-%d")
        with self._conn:
            cur = self._conn.execute(
                "DELETE FROM ip_checks WHERE date < date(?, ?)",
                (cutoff_str, f"-{days_to_keep} days")
            )
        return cur.rowcount


# Singleton — создаём один раз при старте приложения
_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter(daily_limit=_FREE_LIMIT)
    return _limiter
