import gzip
import json
import os
from pathlib import Path

DATA_DIR = os.environ.get("SEATS_DATA_DIR", "plane-strategies-data/data")


def load_fares(folder=DATA_DIR):
    fares = []
    for path in sorted(Path(folder).glob("*/*.json.gz")):
        with gzip.open(path, "rt") as f:
            row = json.load(f)
        if row["status"] != "ok":
            continue
        for fare in row["fares"]:
            fares.append(dict(fare, block=row["block"], depart_date=row["depart_date"],
                              snapshot_date=row["snapshot_date"], lead_days=row["lead_days"]))
    return fares
