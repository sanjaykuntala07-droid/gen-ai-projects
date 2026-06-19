"""
Dream Machine — SQLite Database Layer v2
Normalized relational schemas (Cascade deletes, unique voting, user tracking),
cached DB initializer, bulk fetching logic, and automatic v1-to-v2 data migration.
"""
import sqlite3
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

# DB file lives alongside the app
DB_PATH = Path(__file__).parent.parent / "dream_machine.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")     # Concurrent reads
    conn.execute("PRAGMA synchronous=NORMAL")    # Faster writes
    conn.execute("PRAGMA cache_size=-32000")     # 32MB page cache
    conn.execute("PRAGMA foreign_keys=ON")       # Enforce FK constraints
    conn.row_factory = sqlite3.Row
    return conn


def get_user_session_hash() -> str:
    """Get a SHA-256 hash of the current Streamlit session ID, or a fallback if running outside Streamlit."""
    try:
        import streamlit as st
        if hasattr(st, "context") and hasattr(st.context, "session_id") and st.context.session_id:
            sid = st.context.session_id
        elif hasattr(st, "runtime") and st.runtime.exists():
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            ctx = get_script_run_ctx()
            sid = ctx.session_id if ctx else "default_session"
        else:
            sid = "default_session"
    except Exception:
        sid = "default_session"
        
    return hashlib.sha256(sid.encode()).hexdigest()


def get_current_user_id() -> str:
    """Get the current authenticated user's UUID, creating it if it doesn't exist."""
    session_hash = get_user_session_hash()
    conn = get_conn()
    row = conn.execute("SELECT id FROM users WHERE session_hash=?", (session_hash,)).fetchone()
    if row:
        uid = row["id"]
        # Update last seen
        conn.execute("UPDATE users SET last_seen_at=? WHERE id=?", (datetime.utcnow().isoformat(), uid))
        conn.commit()
        conn.close()
        return uid
        
    # Create new user
    uid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO users (id, session_hash, display_name, created_at, last_seen_at) VALUES (?, ?, ?, ?, ?)",
        (uid, session_hash, "User " + session_hash[:6], now, now)
    )
    conn.commit()
    conn.close()
    return uid


def _init_db_uncached():
    """Create all tables and perform migration if migrating from v1 database."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    c = conn.cursor()

    # Disable foreign keys temporarily for creation & migration
    c.execute("PRAGMA foreign_keys=OFF")

    # 1. Create users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id           TEXT PRIMARY KEY,
        session_hash TEXT NOT NULL UNIQUE,
        display_name TEXT,
        created_at   TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        blueprint_count INTEGER DEFAULT 0
    );
    """)

    # 2. Create idea_types table
    c.execute("""
    CREATE TABLE IF NOT EXISTS idea_types (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        icon TEXT NOT NULL DEFAULT '💡'
    );
    """)

    # Seed default types
    default_types = [
        ('SaaS Platform','🖥️'), ('Mobile App','📱'), ('Physical Product','📦'),
        ('Workflow Automation','⚙️'), ('Business Concept','💼'), ('Social Cause','🌍'),
        ('AI Tool','🤖'), ('Game','🎮'), ('Marketplace','🛒'),
        ('Service Business','🤝'), ('Hardware Device','🔌'), ('Content Platform','🎬'),
        ('Browser Extension','🧩'), ('API / Developer Tool','🔧'),
        ('E-commerce','🛍️'), ('Other','💡')
    ]
    for name, icon in default_types:
        c.execute("INSERT OR IGNORE INTO idea_types (name, icon) VALUES (?, ?)", (name, icon))

    # 3. Create idea_captures table
    c.execute("""
    CREATE TABLE IF NOT EXISTS idea_captures (
        id              TEXT PRIMARY KEY,
        user_id         TEXT REFERENCES users(id) ON DELETE SET NULL,
        raw_text        TEXT NOT NULL,
        source          TEXT DEFAULT 'text',
        mini_blueprint  TEXT DEFAULT '',
        mindmap_code    TEXT DEFAULT '',
        created_at      TEXT NOT NULL
    );
    """)

    # 4. Check if migration from v1 (JSON blobs in blueprints) is needed
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='blueprints'")
    table_exists = c.fetchone()

    migration_needed = False
    if table_exists:
        c.execute("PRAGMA table_info(blueprints)")
        columns = [col[1] for col in c.fetchall()]
        if 'answers_json' in columns:
            migration_needed = True

    if migration_needed:
        # Create a backup of the DB file before migration
        import shutil
        backup_path = DB_PATH.with_suffix(".db.bak")
        if not backup_path.exists():
            try:
                shutil.copy2(DB_PATH, backup_path)
            except Exception:
                pass

        # Create legacy user in users table
        now_str = datetime.utcnow().isoformat()
        c.execute("INSERT OR IGNORE INTO users (id, session_hash, display_name, created_at, last_seen_at) VALUES (?, ?, ?, ?, ?)",
                  ('default_user', 'default_hash', 'Legacy User', now_str, now_str))

        # Rename blueprints table
        c.execute("ALTER TABLE blueprints RENAME TO blueprints_old")

        # Create new normalized blueprints table
        c.execute("""
        CREATE TABLE blueprints (
            id              TEXT PRIMARY KEY,
            user_id         TEXT REFERENCES users(id) ON DELETE CASCADE,
            idea_type_id    INTEGER REFERENCES idea_types(id) ON DELETE SET NULL,
            title           TEXT NOT NULL,
            idea            TEXT NOT NULL,
            status          TEXT DEFAULT 'draft' CHECK(status IN ('draft','generating','complete','archived','in_progress','built')),
            is_public       INTEGER DEFAULT 0 CHECK(is_public IN (0,1)),
            stars           INTEGER DEFAULT 0 CHECK(stars >= 0),
            capture_id      TEXT REFERENCES idea_captures(id) ON DELETE SET NULL,
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL
        );
        """)

        # Create related normalized tables
        c.execute("""
        CREATE TABLE IF NOT EXISTS blueprint_answers (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            blueprint_id TEXT NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
            question     TEXT NOT NULL,
            answer       TEXT NOT NULL,
            seq          INTEGER NOT NULL DEFAULT 0
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS blueprint_sections (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            blueprint_id TEXT NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
            section_key  TEXT NOT NULL,
            content      TEXT NOT NULL DEFAULT '',
            generated_at TEXT,
            UNIQUE(blueprint_id, section_key)
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS blueprint_assets (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            blueprint_id TEXT NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
            asset_type   TEXT NOT NULL CHECK(asset_type IN ('mockup_html','pitch_deck_json','mindmap')),
            content      TEXT NOT NULL,
            byte_size    INTEGER NOT NULL,
            generated_at TEXT NOT NULL,
            UNIQUE(blueprint_id, asset_type)
        );
        """)

        # Migrate all blueprints data
        c.execute("SELECT * FROM blueprints_old")
        old_rows = c.fetchall()
        
        # Get old columns indices map
        c.execute("PRAGMA table_info(blueprints_old)")
        cols_info = c.fetchall()
        col_names = [col_info[1] for col_info in cols_info]
        
        for row in old_rows:
            row_dict = {col_names[i]: row[i] for i in range(len(col_names))}

            bid = row_dict['id']
            title = row_dict['title']
            idea = row_dict['idea']
            old_idea_type = row_dict.get('idea_type', 'Other')
            answers_json = row_dict.get('answers_json') or '{}'
            sections_json = row_dict.get('sections_json') or '{}'
            mockup_html = row_dict.get('mockup_html') or ''
            created_at = row_dict['created_at']
            updated_at = row_dict['updated_at']
            is_public = row_dict.get('is_public', 0)
            status = row_dict.get('status', 'draft')
            stars = row_dict.get('stars', 0)

            # Map idea type to ID
            c.execute("SELECT id FROM idea_types WHERE name=?", (old_idea_type,))
            it_row = c.fetchone()
            if it_row:
                idea_type_id = it_row[0]
            else:
                c.execute("INSERT INTO idea_types (name) VALUES (?)", (old_idea_type,))
                idea_type_id = c.lastrowid

            # Insert into new blueprints table
            c.execute("""
            INSERT INTO blueprints (id, user_id, idea_type_id, title, idea, status, is_public, stars, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (bid, 'default_user', idea_type_id, title, idea, status, is_public, stars, created_at, updated_at))

            # Decompose answers_json
            try:
                answers = json.loads(answers_json)
                if isinstance(answers, dict):
                    for seq, (question, answer) in enumerate(answers.items()):
                        c.execute("""
                        INSERT INTO blueprint_answers (blueprint_id, question, answer, seq)
                        VALUES (?, ?, ?, ?)
                        """, (bid, question, str(answer), seq))
            except Exception:
                pass

            # Decompose sections_json
            try:
                sections = json.loads(sections_json)
                if isinstance(sections, dict):
                    for skey, scontent in sections.items():
                        if scontent:
                            c.execute("""
                            INSERT INTO blueprint_sections (blueprint_id, section_key, content, generated_at)
                            VALUES (?, ?, ?, ?)
                            """, (bid, skey, scontent, updated_at))
            except Exception:
                pass

            # Extract mockup_html
            if mockup_html:
                c.execute("""
                INSERT INTO blueprint_assets (blueprint_id, asset_type, content, byte_size, generated_at)
                VALUES (?, 'mockup_html', ?, ?, ?)
                """, (bid, mockup_html, len(mockup_html.encode('utf-8')), updated_at))

        # Drop old blueprints table
        c.execute("DROP TABLE blueprints_old")

    else:
        # Standard schema creation
        c.execute("""
        CREATE TABLE IF NOT EXISTS blueprints (
            id              TEXT PRIMARY KEY,
            user_id         TEXT REFERENCES users(id) ON DELETE CASCADE,
            idea_type_id    INTEGER REFERENCES idea_types(id) ON DELETE SET NULL,
            title           TEXT NOT NULL,
            idea            TEXT NOT NULL,
            status          TEXT DEFAULT 'draft' CHECK(status IN ('draft','generating','complete','archived','in_progress','built')),
            is_public       INTEGER DEFAULT 0 CHECK(is_public IN (0,1)),
            stars           INTEGER DEFAULT 0 CHECK(stars >= 0),
            capture_id      TEXT REFERENCES idea_captures(id) ON DELETE SET NULL,
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS blueprint_answers (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            blueprint_id TEXT NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
            question     TEXT NOT NULL,
            answer       TEXT NOT NULL,
            seq          INTEGER NOT NULL DEFAULT 0
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS blueprint_sections (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            blueprint_id TEXT NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
            section_key  TEXT NOT NULL,
            content      TEXT NOT NULL DEFAULT '',
            generated_at TEXT,
            UNIQUE(blueprint_id, section_key)
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS blueprint_assets (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            blueprint_id TEXT NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
            asset_type   TEXT NOT NULL CHECK(asset_type IN ('mockup_html','pitch_deck_json','mindmap')),
            content      TEXT NOT NULL,
            byte_size    INTEGER NOT NULL,
            generated_at TEXT NOT NULL,
            UNIQUE(blueprint_id, asset_type)
        );
        """)

    # 5. Create auxiliary tables
    c.execute("""
    CREATE TABLE IF NOT EXISTS gallery_votes (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        blueprint_id TEXT NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
        user_id      TEXT REFERENCES users(id) ON DELETE CASCADE,
        voted_at     TEXT NOT NULL,
        UNIQUE(blueprint_id, user_id)
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS notebooks (
        blueprint_id TEXT PRIMARY KEY REFERENCES blueprints(id) ON DELETE CASCADE,
        notes        TEXT DEFAULT '',
        highlights   TEXT DEFAULT '[]',
        updated_at   TEXT NOT NULL
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        blueprint_id TEXT NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
        role         TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
        content      TEXT NOT NULL,
        created_at   TEXT NOT NULL
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id          TEXT PRIMARY KEY,
        user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        note_text   TEXT NOT NULL,
        importance  TEXT DEFAULT 'Medium' CHECK(importance IN ('Low','Medium','High','Critical')),
        remind_at   TEXT,
        is_notified INTEGER DEFAULT 0 CHECK(is_notified IN (0,1)),
        created_at  TEXT NOT NULL
    );
    """)

    # Re-enable foreign keys
    c.execute("PRAGMA foreign_keys=ON")

    # Indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_blueprints_created ON blueprints(created_at DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_blueprints_public ON blueprints(is_public)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_chat_blueprint ON chat_history(blueprint_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_captures_created ON idea_captures(created_at DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_reminders_remind ON reminders(remind_at) WHERE is_notified = 0")

    conn.commit()
    conn.close()


# Cached initializer (Optimizes performance by running only once per process)
try:
    import streamlit as st
    init_db = st.cache_resource(_init_db_uncached)
except Exception:
    init_db = _init_db_uncached


# ─────────────────────────────────────────────
# BLUEPRINTS CRUD
# ─────────────────────────────────────────────

def create_blueprint(idea: str, idea_type: str, answers: dict) -> str:
    """Create a new blueprint record and return its ID."""
    bid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    uid = get_current_user_id()
    title = idea[:60] + "..." if len(idea) > 60 else idea

    conn = get_conn()
    c = conn.cursor()

    # Fetch/Create idea type mapping ID
    c.execute("SELECT id FROM idea_types WHERE name=?", (idea_type,))
    it_row = c.fetchone()
    if it_row:
        idea_type_id = it_row[0]
    else:
        c.execute("INSERT INTO idea_types (name) VALUES (?)", (idea_type,))
        idea_type_id = c.lastrowid

    # Insert main metadata
    c.execute(
        """INSERT INTO blueprints
           (id, user_id, idea_type_id, title, idea, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (bid, uid, idea_type_id, title, idea, now, now)
    )

    # Insert answers
    for seq, (question, answer) in enumerate(answers.items()):
        c.execute(
            """INSERT INTO blueprint_answers (blueprint_id, question, answer, seq)
               VALUES (?, ?, ?, ?)""",
            (bid, question, str(answer), seq)
        )

    conn.commit()
    conn.close()
    return bid


def update_blueprint_sections(bid: str, sections: dict):
    """Save/update sections associated with a blueprint."""
    now = datetime.utcnow().isoformat()
    conn = get_conn()
    c = conn.cursor()

    for skey, scontent in sections.items():
        c.execute(
            """INSERT INTO blueprint_sections (blueprint_id, section_key, content, generated_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(blueprint_id, section_key) DO UPDATE SET
               content=excluded.content, generated_at=excluded.generated_at""",
            (bid, skey, scontent, now)
        )

    c.execute("UPDATE blueprints SET updated_at=? WHERE id=?", (now, bid))
    conn.commit()
    conn.close()


def update_blueprint_mockup(bid: str, html: str):
    """Save/update the mockup asset associated with a blueprint."""
    now = datetime.utcnow().isoformat()
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        """INSERT INTO blueprint_assets (blueprint_id, asset_type, content, byte_size, generated_at)
           VALUES (?, 'mockup_html', ?, ?, ?)
           ON CONFLICT(blueprint_id, asset_type) DO UPDATE SET
           content=excluded.content, byte_size=excluded.byte_size, generated_at=excluded.generated_at""",
        (bid, html, len(html.encode('utf-8')), now)
    )

    c.execute("UPDATE blueprints SET updated_at=? WHERE id=?", (now, bid))
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
    """Fetch complete blueprint and reconstruct v1 dict format for compatibility."""
    conn = get_conn()
    row = conn.execute("""
        SELECT b.*, t.name as idea_type
        FROM blueprints b
        LEFT JOIN idea_types t ON b.idea_type_id = t.id
        WHERE b.id = ?
    """, (bid,)).fetchone()
    
    if not row:
        conn.close()
        return None
        
    d = dict(row)
    
    # Reconstruct answers
    ans_rows = conn.execute("SELECT question, answer FROM blueprint_answers WHERE blueprint_id = ? ORDER BY seq ASC", (bid,)).fetchall()
    answers = {r["question"]: r["answer"] for r in ans_rows}
    d["answers"] = answers
    d["answers_json"] = json.dumps(answers)
    
    # Reconstruct sections
    sec_rows = conn.execute("SELECT section_key, content FROM blueprint_sections WHERE blueprint_id = ?", (bid,)).fetchall()
    sections = {r["section_key"]: r["content"] for r in sec_rows}
    d["sections"] = sections
    d["sections_json"] = json.dumps(sections)
    
    # Reconstruct mockup_html
    asset_row = conn.execute("SELECT content FROM blueprint_assets WHERE blueprint_id = ? AND asset_type = 'mockup_html'", (bid,)).fetchone()
    d["mockup_html"] = asset_row["content"] if asset_row else ""
    
    conn.close()
    return d


def list_blueprints(limit: int = 100, all_users: bool = False) -> list[dict]:
    """List blueprints for current user session (or all users if specified) in bulk."""
    uid = get_current_user_id()
    conn = get_conn()
    
    if all_users:
        rows = conn.execute("""
            SELECT b.*, t.name as idea_type
            FROM blueprints b
            LEFT JOIN idea_types t ON b.idea_type_id = t.id
            ORDER BY b.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT b.*, t.name as idea_type
            FROM blueprints b
            LEFT JOIN idea_types t ON b.idea_type_id = t.id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
            LIMIT ?
        """, (uid, limit)).fetchall()
        
    if not rows:
        conn.close()
        return []
        
    result = []
    bids = [r["id"] for r in rows]
    placeholders = ",".join(["?"] * len(bids))
    
    # Bulk fetch answers
    ans_rows = conn.execute(f"""
        SELECT blueprint_id, question, answer 
        FROM blueprint_answers 
        WHERE blueprint_id IN ({placeholders})
        ORDER BY seq ASC
    """, bids).fetchall()
    
    answers_by_bp = {}
    for r in ans_rows:
        answers_by_bp.setdefault(r["blueprint_id"], {})[r["question"]] = r["answer"]
        
    # Bulk fetch sections
    sec_rows = conn.execute(f"""
        SELECT blueprint_id, section_key, content 
        FROM blueprint_sections 
        WHERE blueprint_id IN ({placeholders})
    """, bids).fetchall()
    
    sections_by_bp = {}
    for r in sec_rows:
        sections_by_bp.setdefault(r["blueprint_id"], {})[r["section_key"]] = r["content"]
        
    # Bulk fetch mockup
    asset_rows = conn.execute(f"""
        SELECT blueprint_id, content 
        FROM blueprint_assets 
        WHERE blueprint_id IN ({placeholders}) AND asset_type = 'mockup_html'
    """, bids).fetchall()
    
    mockup_by_bp = {r["blueprint_id"]: r["content"] for r in asset_rows}
    conn.close()
    
    for row in rows:
        d = dict(row)
        bid = d["id"]
        d["answers"] = answers_by_bp.get(bid, {})
        d["answers_json"] = json.dumps(d["answers"])
        d["sections"] = sections_by_bp.get(bid, {})
        d["sections_json"] = json.dumps(d["sections"])
        d["mockup_html"] = mockup_by_bp.get(bid, "")
        result.append(d)
        
    return result


def list_public_blueprints(limit: int = 50) -> list[dict]:
    """List public blueprints from all users (Gallery display)."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT b.*, t.name as idea_type
        FROM blueprints b
        LEFT JOIN idea_types t ON b.idea_type_id = t.id
        WHERE b.is_public = 1
        ORDER BY b.stars DESC, b.created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    
    if not rows:
        conn.close()
        return []
        
    bids = [r["id"] for r in rows]
    placeholders = ",".join(["?"] * len(bids))
    
    sec_rows = conn.execute(f"""
        SELECT blueprint_id, section_key, content 
        FROM blueprint_sections 
        WHERE blueprint_id IN ({placeholders})
    """, bids).fetchall()
    
    sections_by_bp = {}
    for r in sec_rows:
        sections_by_bp.setdefault(r["blueprint_id"], {})[r["section_key"]] = r["content"]
        
    conn.close()
    
    result = []
    for row in rows:
        d = dict(row)
        bid = d["id"]
        d["sections"] = sections_by_bp.get(bid, {})
        d["sections_json"] = json.dumps(d["sections"])
        result.append(d)
        
    return result


def delete_blueprint(bid: str):
    """Deletes a blueprint, cascades constraints on FK."""
    conn = get_conn()
    conn.execute("DELETE FROM blueprints WHERE id=?", (bid,))
    conn.commit()
    conn.close()


def star_blueprint(bid: str):
    """Vote for a blueprint with unique user constraints (Deduplication)."""
    conn = get_conn()
    uid = get_current_user_id()
    now = datetime.utcnow().isoformat()
    
    # Deduplicated at database level, triggers handle the stars counter auto-increment
    conn.execute(
        "INSERT OR IGNORE INTO gallery_votes (blueprint_id, user_id, voted_at) VALUES (?, ?, ?)",
        (bid, uid, now)
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
# IDEA CAPTURES
# ─────────────────────────────────────────────

def save_capture(raw_text: str, source: str = "text",
                 mini_blueprint: str = "", mindmap_code: str = "") -> str:
    """Save an idea capture, linked to user session."""
    cid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    uid = get_current_user_id()
    conn = get_conn()
    conn.execute(
        """INSERT INTO idea_captures (id, user_id, raw_text, source, mini_blueprint, mindmap_code, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (cid, uid, raw_text, source, mini_blueprint, mindmap_code, now)
    )
    conn.commit()
    conn.close()
    return cid


def update_capture(cid: str, mini_blueprint: str = "", mindmap_code: str = ""):
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
    """List captures belonging to the active session user."""
    uid = get_current_user_id()
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM idea_captures WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
        (uid, limit)
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
    """Create a new user reminder note."""
    rid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    uid = get_current_user_id()
    conn = get_conn()
    conn.execute(
        """INSERT INTO reminders (id, user_id, note_text, importance, remind_at, is_notified, created_at)
           VALUES (?, ?, ?, ?, ?, 0, ?)""",
        (rid, uid, note_text, importance, remind_at, now)
    )
    conn.commit()
    conn.close()
    return rid


def list_reminders(limit: int = 100) -> list[dict]:
    """List all reminders for current user session."""
    uid = get_current_user_id()
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM reminders WHERE user_id=? ORDER BY is_notified ASC, datetime(remind_at) ASC, created_at DESC LIMIT ?",
        (uid, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_reminder_notified(rid: str):
    conn = get_conn()
    conn.execute("UPDATE reminders SET is_notified = 1 WHERE id = ?", (rid,))
    conn.commit()
    conn.close()


def delete_reminder(rid: str):
    conn = get_conn()
    conn.execute("DELETE FROM reminders WHERE id = ?", (rid,))
    conn.commit()
    conn.close()
