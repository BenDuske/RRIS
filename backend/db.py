import sqlite3
import json
import os
from datetime import datetime, timezone
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rris.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS incidents (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                status        TEXT DEFAULT 'active',
                incident_type TEXT,
                location_lat  REAL,
                location_lng  REAL,
                location_desc TEXT,
                location_radius INTEGER DEFAULT 50,
                priority      INTEGER,
                confidence    REAL,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS events (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id     TEXT,
                source_type   TEXT,
                raw_text      TEXT,
                parsed_fields TEXT,
                confidence    REAL,
                provenance    TEXT,
                location_lat  REAL,
                location_lng  REAL,
                received_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS incident_events (
                incident_id   INTEGER REFERENCES incidents(id),
                event_id      INTEGER REFERENCES events(id),
                attached_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                match_score   REAL,
                PRIMARY KEY (incident_id, event_id)
            );

            CREATE TABLE IF NOT EXISTS timeline_entries (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id   INTEGER REFERENCES incidents(id),
                entry_type    TEXT,
                summary       TEXT,
                delta_fields  TEXT,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sources (
                id            TEXT PRIMARY KEY,
                name          TEXT,
                source_type   TEXT,
                reliability   REAL DEFAULT 0.8,
                last_polled   TIMESTAMP,
                status        TEXT DEFAULT 'active'
            );
        """)
        for source_id, name, stype, reliability in [
            ("nws", "National Weather Service", "api", 1.0),
            ("txdot", "TxDOT Traffic", "api", 0.9),
            ("cad_sim", "Simulated 911/CAD", "simulated", 0.85),
            ("manual", "Field Report", "manual", 0.7),
        ]:
            conn.execute(
                "INSERT OR IGNORE INTO sources (id, name, source_type, reliability) VALUES (?, ?, ?, ?)",
                (source_id, name, stype, reliability),
            )


# --- Event CRUD ---

def insert_event(conn, event) -> int:
    parsed = event.parsed_fields.model_dump() if event.parsed_fields else {}
    prov = event.provenance.model_dump() if event.provenance else {}
    # Serialize datetimes in provenance
    for k, v in prov.items():
        if isinstance(v, datetime):
            prov[k] = v.isoformat()

    cursor = conn.execute(
        """INSERT INTO events (source_id, source_type, raw_text, parsed_fields,
           confidence, provenance, location_lat, location_lng, received_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            event.source_id,
            event.source_type,
            event.raw_text,
            json.dumps(parsed, default=str),
            event.confidence,
            json.dumps(prov, default=str),
            event.location.lat,
            event.location.lng,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    return cursor.lastrowid


def get_event(conn, event_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["parsed_fields"] = json.loads(d["parsed_fields"]) if d["parsed_fields"] else {}
    d["provenance"] = json.loads(d["provenance"]) if d["provenance"] else {}
    return d


# --- Incident CRUD ---

def insert_incident(conn, incident_type, lat, lng, address, radius=50, priority=None, confidence=None) -> int:
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        """INSERT INTO incidents (incident_type, location_lat, location_lng, location_desc,
           location_radius, priority, confidence, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (incident_type, lat, lng, address, radius, priority, confidence, now, now),
    )
    return cursor.lastrowid


def update_incident(conn, incident_id: int, **fields):
    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [incident_id]
    conn.execute(f"UPDATE incidents SET {set_clause} WHERE id = ?", values)


def get_incident(conn, incident_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["events"] = get_incident_events(conn, incident_id)
    d["timeline"] = get_timeline(conn, incident_id)
    return d


def get_all_incidents(conn, status: str = None) -> list[dict]:
    if status:
        rows = conn.execute("SELECT * FROM incidents WHERE status = ? ORDER BY priority DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM incidents ORDER BY priority DESC").fetchall()

    results = []
    for row in rows:
        d = dict(row)
        d["events"] = get_incident_events(conn, d["id"])
        d["timeline"] = get_timeline(conn, d["id"])
        results.append(d)
    return results


# --- Incident ↔ Event linking ---

def link_event_to_incident(conn, incident_id: int, event_id: int, match_score: float = 1.0):
    conn.execute(
        "INSERT OR IGNORE INTO incident_events (incident_id, event_id, match_score) VALUES (?, ?, ?)",
        (incident_id, event_id, match_score),
    )


def get_incident_events(conn, incident_id: int) -> list[dict]:
    rows = conn.execute(
        """SELECT e.*, ie.match_score, ie.attached_at
           FROM events e
           JOIN incident_events ie ON e.id = ie.event_id
           WHERE ie.incident_id = ?
           ORDER BY e.received_at""",
        (incident_id,),
    ).fetchall()
    results = []
    for row in rows:
        d = dict(row)
        d["parsed_fields"] = json.loads(d["parsed_fields"]) if d["parsed_fields"] else {}
        d["provenance"] = json.loads(d["provenance"]) if d["provenance"] else {}
        results.append(d)
    return results


# --- Timeline ---

def add_timeline_entry(conn, incident_id: int, entry_type: str, summary: str, delta_fields: dict = None):
    conn.execute(
        "INSERT INTO timeline_entries (incident_id, entry_type, summary, delta_fields) VALUES (?, ?, ?, ?)",
        (incident_id, entry_type, summary, json.dumps(delta_fields, default=str) if delta_fields else None),
    )


def get_timeline(conn, incident_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM timeline_entries WHERE incident_id = ? ORDER BY created_at",
        (incident_id,),
    ).fetchall()
    results = []
    for row in rows:
        d = dict(row)
        d["delta_fields"] = json.loads(d["delta_fields"]) if d["delta_fields"] else None
        results.append(d)
    return results


# --- Sources ---

def get_sources(conn) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM sources").fetchall()]


def update_source_poll(conn, source_id: str):
    conn.execute(
        "UPDATE sources SET last_polled = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), source_id),
    )


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {os.path.abspath(DB_PATH)}")
