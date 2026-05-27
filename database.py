"""
database.py — SQLite storage layer for Study Notes Manager
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import Optional

# Render e deploy korle /data/notes.db use hobe, local e notes.db
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "notes.db"))


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                content     TEXT    NOT NULL,
                summary     TEXT    DEFAULT '',
                keywords    TEXT    DEFAULT '[]',
                tags        TEXT    DEFAULT '',
                quiz        TEXT    DEFAULT '[]',
                created_at  TEXT    NOT NULL,
                updated_at  TEXT    NOT NULL
            )
        """)
        conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def create_note(title, content, summary='', keywords=None, tags='', quiz=None) -> int:
    now = _now()
    with _get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title,content,summary,keywords,tags,quiz,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)",
            (title, content, summary, json.dumps(keywords or []), tags, json.dumps(quiz or []), now, now),
        )
        conn.commit()
        return cur.lastrowid


def _row_to_dict(row):
    d = dict(row)
    d['keywords'] = json.loads(d.get('keywords') or '[]')
    d['quiz']     = json.loads(d.get('quiz')     or '[]')
    return d


def get_note(note_id: int):
    with _get_conn() as conn:
        row = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    return _row_to_dict(row) if row else None


def get_all_notes() -> list:
    with _get_conn() as conn:
        rows = conn.execute('SELECT * FROM notes ORDER BY updated_at DESC').fetchall()
    return [_row_to_dict(r) for r in rows]


def search_notes(query: str) -> list:
    like = f'%{query}%'
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR keywords LIKE ? OR tags LIKE ? ORDER BY updated_at DESC",
            (like, like, like, like),
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def update_note(note_id, title, content, summary='', keywords=None, tags='', quiz=None) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "UPDATE notes SET title=?,content=?,summary=?,keywords=?,tags=?,quiz=?,updated_at=? WHERE id=?",
            (title, content, summary, json.dumps(keywords or []), tags, json.dumps(quiz or []), _now(), note_id),
        )
        conn.commit()
        return cur.rowcount > 0


def delete_note(note_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
        return cur.rowcount > 0