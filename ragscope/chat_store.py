from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime


class ChatStore:
    """Lưu lượt hỏi theo từng người dùng (mỗi người một phiên riêng) bằng SQLite.

    Vai trò:
    - Tách phiên: mọi truy vấn đều lọc theo user_id nên không lẫn lịch sử giữa
      các vai trò/bối cảnh khác nhau.
    - Giữ ngữ cảnh: câu hỏi tiếp theo ("vậy thì sao?") có thể mở rộng từ lượt hỏi
      trước mà không cần hiện lại lịch sử lên giao diện.
    """

    def __init__(self, path: str):
        self.path = path
        folder = os.path.dirname(os.path.abspath(path))
        if folder:
            os.makedirs(folder, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_name TEXT,
                    unit TEXT,
                    question TEXT NOT NULL,
                    effective_question TEXT,
                    answer_kind TEXT,
                    answer_text TEXT,
                    reason TEXT,
                    sources TEXT,
                    scope TEXT,
                    as_of TEXT,
                    used_context TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_turns_user ON turns(user_id, id)"
            )
            self._migrate()
            self._conn.commit()

    def _migrate(self) -> None:
        """Thêm cột mới nếu bảng cũ đã tồn tại từ phiên bản trước."""
        cols = {r["name"] for r in self._conn.execute("PRAGMA table_info(turns)").fetchall()}
        if "scope" not in cols:
            self._conn.execute("ALTER TABLE turns ADD COLUMN scope TEXT")

    def add_turn(self, user_id, user_name, unit, question, effective_question,
                 answer_kind, answer_text, reason, sources, as_of, used_context,
                 scope=None) -> int:
        with self._lock:
            cur = self._conn.execute(
                """
                INSERT INTO turns (user_id, user_name, unit, question, effective_question,
                                   answer_kind, answer_text, reason, sources, scope, as_of,
                                   used_context, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    user_id,
                    user_name,
                    unit,
                    question,
                    effective_question,
                    answer_kind,
                    answer_text,
                    reason,
                    json.dumps(sources, ensure_ascii=False, default=str),
                    json.dumps(scope or {}, ensure_ascii=False, default=str),
                    as_of.isoformat() if hasattr(as_of, "isoformat") else str(as_of),
                    json.dumps(used_context, ensure_ascii=False, default=str),
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            self._conn.commit()
            return int(cur.lastrowid)

    def recent_turns(self, user_id, limit: int = 5) -> list:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM turns WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        turns = [dict(r) for r in rows]
        for t in turns:
            try:
                t["sources"] = json.loads(t["sources"] or "[]")
            except (TypeError, ValueError):
                t["sources"] = []
            try:
                t["used_context"] = json.loads(t["used_context"] or "[]")
            except (TypeError, ValueError):
                t["used_context"] = []
            try:
                t["scope"] = json.loads(t["scope"] or "{}")
            except (TypeError, ValueError):
                t["scope"] = {}
        return list(reversed(turns))

    def count(self, user_id) -> int:
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) AS c FROM turns WHERE user_id = ?", (user_id,)
            ).fetchone()
        return int(row["c"]) if row else 0

    def clear(self, user_id) -> int:
        with self._lock:
            cur = self._conn.execute("DELETE FROM turns WHERE user_id = ?", (user_id,))
            self._conn.commit()
            return cur.rowcount

    def close(self) -> None:
        with self._lock:
            self._conn.close()
