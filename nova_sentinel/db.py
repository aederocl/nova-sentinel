from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from .models import Candidate

SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
  fingerprint TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  source_id TEXT,
  name TEXT NOT NULL,
  ra_deg REAL,
  dec_deg REAL,
  magnitude REAL,
  discovery_time TEXT,
  url TEXT,
  comments TEXT,
  score INTEGER NOT NULL,
  reasons_json TEXT NOT NULL,
  raw_json TEXT NOT NULL,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  alerted INTEGER NOT NULL DEFAULT 0
);
"""

class Store:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(SCHEMA)
        self.connection.commit()

    def upsert(self, c: Candidate) -> tuple[bool, bool]:
        now = datetime.now(timezone.utc).isoformat()
        old = self.connection.execute(
            "SELECT score, alerted FROM candidates WHERE fingerprint=?", (c.fingerprint,)
        ).fetchone()
        is_new = old is None
        previously_alerted = bool(old["alerted"]) if old else False
        self.connection.execute(
            """INSERT INTO candidates VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(fingerprint) DO UPDATE SET
              source=excluded.source, source_id=excluded.source_id, name=excluded.name,
              ra_deg=excluded.ra_deg, dec_deg=excluded.dec_deg, magnitude=excluded.magnitude,
              discovery_time=excluded.discovery_time, url=excluded.url, comments=excluded.comments,
              score=excluded.score, reasons_json=excluded.reasons_json, raw_json=excluded.raw_json,
              last_seen=excluded.last_seen""",
            (c.fingerprint, c.source, c.source_id, c.name, c.ra_deg, c.dec_deg, c.magnitude,
             c.discovery_time.isoformat() if c.discovery_time else None, c.url, c.comments,
             c.score, json.dumps(c.reasons), json.dumps(c.raw), now, now, int(previously_alerted)),
        )
        self.connection.commit()
        score_increased = old is not None and c.score > old["score"]
        return is_new, score_increased

    def mark_alerted(self, fingerprint: str) -> None:
        self.connection.execute("UPDATE candidates SET alerted=1 WHERE fingerprint=?", (fingerprint,))
        self.connection.commit()

    def recent(self, limit: int = 100) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT * FROM candidates ORDER BY first_seen DESC LIMIT ?", (limit,)
        ).fetchall()
