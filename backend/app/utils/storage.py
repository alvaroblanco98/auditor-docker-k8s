import json
import os
from datetime import datetime, timezone

DB_PATH = "results.json"

def load_all_results():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_result(entry: dict):
    data = load_all_results()
    data.append({
        "id": len(data) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **entry
    })
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
