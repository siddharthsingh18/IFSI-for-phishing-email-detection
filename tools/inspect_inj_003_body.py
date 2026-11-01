import json
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

with open("data/evaluation/phase5_regression_160.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["sample_id"] == "gen-inj-003":
            print("Subject:", r.get("subject"))
            print("Body:\n", r.get("body"))

