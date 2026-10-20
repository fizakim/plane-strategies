import gzip
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
    id INTEGER PRIMARY KEY,
    block TEXT NOT NULL,
    depart_date TEXT NOT NULL,
    lead_days INTEGER NOT NULL,
    snapshot_date TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    status TEXT NOT NULL,
    error TEXT,
    n_fares INTEGER NOT NULL,
    params TEXT NOT NULL,
    raw BLOB
);
CREATE INDEX IF NOT EXISTS calls_key ON calls (block, depart_date, snapshot_date);

CREATE TABLE IF NOT EXISTS fares (
    call_id INTEGER NOT NULL REFERENCES calls (id),
    airline TEXT NOT NULL,
    flight_number TEXT NOT NULL,
    origin TEXT NOT NULL,
    dest TEXT NOT NULL,
    dep_time TEXT NOT NULL,
    airplane TEXT,
    price REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS fares_call ON fares (call_id);
"""


class Store:
    def __init__(self, path):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)

    def already_done(self, block, depart_date, snapshot_date):
        row = self.db.execute(
            "SELECT 1 FROM calls WHERE block=? AND depart_date=? AND snapshot_date=? AND status='ok'",
            (block, depart_date, snapshot_date),
        ).fetchone()
        return row is not None

    def save(self, block, depart_date, lead_days, snapshot_date, params, data, error, fares):
        raw = None
        if data is not None:
            raw = gzip.compress(json.dumps(data).encode())
        status = "error" if error else "ok"
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cur = self.db.execute(
            "INSERT INTO calls (block, depart_date, lead_days, snapshot_date, fetched_at,"
            " status, error, n_fares, params, raw) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (block, depart_date, lead_days, snapshot_date, fetched_at,
             status, error, len(fares), json.dumps(params), raw),
        )
        rows = []
        for f in fares:
            rows.append((cur.lastrowid, f.airline, f.flight_number, f.origin, f.dest,
                         f.dep_time, f.airplane, f.price))
        self.db.executemany("INSERT INTO fares VALUES (?,?,?,?,?,?,?,?)", rows)
        self.db.commit()
