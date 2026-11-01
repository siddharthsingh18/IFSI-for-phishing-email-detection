import json
from pathlib import Path

p = Path("results/phase5_a1_sanitizer_latency/predictions.jsonl")
if not p.exists():
    print("File does not exist")
else:
    counts = {}
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                cid = r.get("config_id")
                counts[cid] = counts.get(cid, 0) + 1
    print("Current predictions:", counts)

