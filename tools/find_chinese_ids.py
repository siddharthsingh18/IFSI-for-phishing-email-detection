import json

with open("data/evaluation/a1_generalization_v1.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        if "95588" in row.get("body", "") or "系统最高指令" in row.get("body", ""):
            print("Found sample_id:", row.get("id") or row.get("sample_id"))

