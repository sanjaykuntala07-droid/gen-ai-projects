"""
Dream Machine — SQLite Database Layer
Full CRUD for blueprints, gallery, notebooks.
"""
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path

# DB file lives alongside the app
DB_PATH = Path(__file__).parent.parent / "dream_machine.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")   # Concurrent reads
    conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
    conn.execute("PRAGMA cache_size=-32000")   # 32MB page cache
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS blueprints (
        id          TEXT PRIMARY KEY,
        title       TEXT NOT NULL,
        idea        TEXT NOT NULL,
        idea_type   TEXT DEFAULT 'Unknown',
        answers_json TEXT DEFAULT '{}',
        sections_json TEXT DEFAULT '{}',
        mockup_html  TEXT DEFAULT '',
        created_at  TEXT NOT NULL,
        updated_at  TEXT NOT NULL,
        is_public   INTEGER DEFAULT 0,
        status      TEXT DEFAULT 'draft',
        stars       INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS gallery_votes (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        blueprint_id TEXT NOT NULL,
        voted_at     TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS notebooks (
        blueprint_id TEXT PRIMARY KEY,
        notes        TEXT DEFAULT '',
        highlights   TEXT DEFAULT '[]',
        updated_at   TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS chat_history (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        blueprint_id TEXT NOT NULL,
        role         TEXT NOT NULL,
        content      TEXT NOT NULL,
        created_at   TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS idea_captures (
        id              TEXT PRIMARY KEY,
        raw_text        TEXT NOT NULL,
        source          TEXT DEFAULT 'text',
        mini_blueprint  TEXT DEFAULT '',
        mindmap_code    TEXT DEFAULT '',
        created_at      TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS reminders (
        id          TEXT PRIMARY KEY,
        note_text   TEXT NOT NULL,
        importance  TEXT DEFAULT 'Medium',
        remind_at   TEXT,
        is_notified INTEGER DEFAULT 0,
        created_at  TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_blueprints_created ON blueprints(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_blueprints_public ON blueprints(is_public);
    CREATE INDEX IF NOT EXISTS idx_chat_blueprint ON chat_history(blueprint_id);
    CREATE INDEX IF NOT EXISTS idx_captures_created ON idea_captures(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_reminders_remind ON reminders(remind_at) WHERE is_notified = 0;
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# BLUEPRINTS
# ─────────────────────────────────────────────

def create_blueprint(idea: str, idea_type: str, answers: dict) -> str:
    """Create a new blueprint record and return its ID."""
    bid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    title = idea[:60] + "..." if len(idea) > 60 else idea

    conn = get_conn()
    conn.execute(
        """INSERT INTO blueprints
           (id, title, idea, idea_type, answers_json, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (bid, title, idea, idea_type, json.dumps(answers), now, now)
    )
    conn.commit()
    conn.close()
    return bid


def update_blueprint_sections(bid: str, sections: dict):
    conn = get_conn()
    conn.execute(
        "UPDATE blueprints SET sections_json=?, updated_at=? WHERE id=?",
        (json.dumps(sections), datetime.utcnow().isoformat(), bid)
    )
    conn.commit()
    conn.close()


def update_blueprint_mockup(bid: str, html: str):
    conn = get_conn()
    conn.execute(
        "UPDATE blueprints SET mockup_html=?, updated_at=? WHERE id=?",
        (html, datetime.utcnow().isoformat(), bid)
    )
    conn.commit()
    conn.close()


def update_blueprint_status(bid: str, status: str):
    conn = get_conn()
    conn.execute(
        "UPDATE blueprints SET status=?, updated_at=? WHERE id=?",
        (status, datetime.utcnow().isoformat(), bid)
    )
    conn.commit()
    conn.close()


def update_blueprint_title(bid: str, title: str):
    conn = get_conn()
    conn.execute(
        "UPDATE blueprints SET title=?, updated_at=? WHERE id=?",
        (title, datetime.utcnow().isoformat(), bid)
    )
    conn.commit()
    conn.close()


def toggle_blueprint_public(bid: str, public: bool):
    conn = get_conn()
    conn.execute(
        "UPDATE blueprints SET is_public=?, updated_at=? WHERE id=?",
        (1 if public else 0, datetime.utcnow().isoformat(), bid)
    )
    conn.commit()
    conn.close()


def get_blueprint(bid: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM blueprints WHERE id=?", (bid,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["answers"] = json.loads(d.get("answers_json") or "{}")
    d["sections"] = json.loads(d.get("sections_json") or "{}")
    return d


def list_blueprints(limit: int = 100) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM blueprints ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["answers"] = json.loads(d.get("answers_json") or "{}")
        d["sections"] = json.loads(d.get("sections_json") or "{}")
        result.append(d)
    return result


def list_public_blueprints(limit: int = 50) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM blueprints WHERE is_public=1 ORDER BY stars DESC, created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["sections"] = json.loads(d.get("sections_json") or "{}")
        result.append(d)
    return result


def delete_blueprint(bid: str):
    conn = get_conn()
    conn.execute("DELETE FROM blueprints WHERE id=?", (bid,))
    conn.execute("DELETE FROM notebooks WHERE blueprint_id=?", (bid,))
    conn.execute("DELETE FROM chat_history WHERE blueprint_id=?", (bid,))
    conn.commit()
    conn.close()


def star_blueprint(bid: str):
    conn = get_conn()
    conn.execute(
        "UPDATE blueprints SET stars = stars + 1 WHERE id=?", (bid,)
    )
    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO gallery_votes (blueprint_id, voted_at) VALUES (?, ?)",
        (bid, now)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# NOTEBOOK
# ─────────────────────────────────────────────

def get_notes(bid: str) -> dict:
    conn = get_conn()
    row = conn.execute("SELECT * FROM notebooks WHERE blueprint_id=?", (bid,)).fetchone()
    conn.close()
    if not row:
        return {"notes": "", "highlights": []}
    d = dict(row)
    d["highlights"] = json.loads(d.get("highlights") or "[]")
    return d


def save_notes(bid: str, notes: str, highlights: list = None):
    now = datetime.utcnow().isoformat()
    hl = json.dumps(highlights or [])
    conn = get_conn()
    conn.execute(
        """INSERT INTO notebooks (blueprint_id, notes, highlights, updated_at)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(blueprint_id) DO UPDATE SET
           notes=excluded.notes, highlights=excluded.highlights, updated_at=excluded.updated_at""",
        (bid, notes, hl, now)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────

def save_chat_message(bid: str, role: str, content: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO chat_history (blueprint_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (bid, role, content, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_chat_history(bid: str, limit: int = 20) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, content, created_at FROM chat_history WHERE blueprint_id=? ORDER BY created_at ASC LIMIT ?",
        (bid, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_chat_history(bid: str):
    conn = get_conn()
    conn.execute("DELETE FROM chat_history WHERE blueprint_id=?", (bid,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# IDEA CAPTURES (Voice + Text Notes)
# ─────────────────────────────────────────────

def save_capture(raw_text: str, source: str = "text",
                 mini_blueprint: str = "", mindmap_code: str = "") -> str:
    """Save a voice/text idea capture. Returns the new capture ID."""
    cid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    conn = get_conn()
    conn.execute(
        """INSERT INTO idea_captures (id, raw_text, source, mini_blueprint, mindmap_code, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (cid, raw_text, source, mini_blueprint, mindmap_code, now)
    )
    conn.commit()
    conn.close()
    return cid


def update_capture(cid: str, mini_blueprint: str = "", mindmap_code: str = ""):
    """Update a capture with generated content."""
    conn = get_conn()
    conn.execute(
        "UPDATE idea_captures SET mini_blueprint=?, mindmap_code=? WHERE id=?",
        (mini_blueprint, mindmap_code, cid)
    )
    conn.commit()
    conn.close()


def get_capture(cid: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM idea_captures WHERE id=?", (cid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_captures(limit: int = 50) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM idea_captures ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_capture(cid: str):
    conn = get_conn()
    conn.execute("DELETE FROM idea_captures WHERE id=?", (cid,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# REMINDERS
# ─────────────────────────────────────────────

def create_reminder(note_text: str, importance: str = "Medium", remind_at: str = None) -> str:
    """Create a new reminder note."""
    rid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    conn = get_conn()
    conn.execute(
        """INSERT INTO reminders (id, note_text, importance, remind_at, is_notified, created_at)
           VALUES (?, ?, ?, ?, 0, ?)""",
        (rid, note_text, importance, remind_at, now)
    )
    conn.commit()
    conn.close()
    return rid


def list_reminders(limit: int = 100) -> list[dict]:
    """List all reminders ordered by target time/creation."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM reminders ORDER BY is_notified ASC, datetime(remind_at) ASC, created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_reminder_notified(rid: str):
    """Mark a reminder as triggered/notified."""
    conn = get_conn()
    conn.execute("UPDATE reminders SET is_notified = 1 WHERE id = ?", (rid,))
    conn.commit()
    conn.close()


def delete_reminder(rid: str):
    """Delete a reminder."""
    conn = get_conn()
    conn.execute("DELETE FROM reminders WHERE id = ?", (rid,))
    conn.commit()
    conn.close()
