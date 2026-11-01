import json
from collections import Counter

counts = Counter()
samples_by_cat = {}

with open("data/evaluation/a1_generalization_v1.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        cat = row.get("category", "unknown")
        sid = row.get("sample_id") or row.get("id")
        counts[cat] += 1
        samples_by_cat.setdefault(cat, []).append(sid)

print("Dataset breakdown by category:")
for cat, cnt in counts.items():
    print(f"  {cat}: {cnt}")

chinese_ids = ["gen-inj-008", "gen-inj-018", "gen-inj-028", "gen-inj-038", "gen-inj-048"]
print(f"\nChinese ids present in active injection: {[cid in samples_by_cat.get('active_prompt_injection', []) for cid in chinese_ids]}")

