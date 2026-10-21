import gzip
import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path


class Store:
    def __init__(self, folder):
        self.folder = Path(folder)

    def path(self, block, depart_date, snapshot_date, extra=""):
        return self.folder / snapshot_date / (block + "_" + depart_date + extra + ".json.gz")

    def already_done(self, block, depart_date, snapshot_date):
        return self.path(block, depart_date, snapshot_date).exists()

    def save(self, block, depart_date, lead_days, snapshot_date, params, data, error, fares):
        now = datetime.now(timezone.utc)
        row = {
            "block": block,
            "depart_date": depart_date,
            "lead_days": lead_days,
            "snapshot_date": snapshot_date,
            "fetched_at": now.isoformat(timespec="seconds"),
            "status": "error" if error else "ok",
            "error": error,
            "params": params,
            "fares": [asdict(f) for f in fares],
            "raw": data,
        }
        extra = ""
        if error:
            extra = "_error_" + now.strftime("%H%M%S")
        path = self.path(block, depart_date, snapshot_date, extra)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = str(path) + ".tmp"
        with gzip.open(tmp, "wt") as f:
            json.dump(row, f)
        os.replace(tmp, path)
