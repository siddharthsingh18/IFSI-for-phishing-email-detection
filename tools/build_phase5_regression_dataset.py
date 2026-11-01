import json
from pathlib import Path

# Load full A1 generalization benchmark (read-only)
all_samples = {}
with open("data/evaluation/a1_generalization_v1.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        sid = row.get("sample_id") or row.get("id")
        all_samples[sid] = row

# 1. 50 active injection samples (including the 5 Chinese samples)
active_injection_samples = [
    sid for sid, row in all_samples.items()
    if row.get("subcategory", "").startswith("active_")
]
assert len(active_injection_samples) == 50, f"Expected 50 active injection samples, got {len(active_injection_samples)}"

chinese_ids = ["gen-inj-008", "gen-inj-018", "gen-inj-028", "gen-inj-038", "gen-inj-048"]
assert all(cid in active_injection_samples for cid in chinese_ids), "All 5 Chinese samples must be in active injection"

# 2. 50 quoted injection samples
quoted_injection_samples = [
    sid for sid, row in all_samples.items()
    if row.get("subcategory", "").startswith("quoted_")
]
assert len(quoted_injection_samples) == 50, f"Expected 50 quoted injection samples, got {len(quoted_injection_samples)}"

# 3. 20 difficult legitimate corrected samples
dif_ids = [
    'gen-dif-001', 'gen-dif-004', 'gen-dif-011', 'gen-dif-014', 'gen-dif-021',
    'gen-dif-024', 'gen-dif-031', 'gen-dif-034', 'gen-dif-041', 'gen-dif-044',
    'gen-dif-051', 'gen-dif-054', 'gen-dif-061', 'gen-dif-064', 'gen-dif-071',
    'gen-dif-074', 'gen-dif-081', 'gen-dif-084', 'gen-dif-091', 'gen-dif-094'
]
assert len(dif_ids) == 20, f"Expected 20 difficult samples, got {len(dif_ids)}"

# 4. 20 sophisticated phishing shared false negatives
sop_ids = [
    'gen-sop-007', 'gen-sop-009', 'gen-sop-017', 'gen-sop-019', 'gen-sop-027',
    'gen-sop-029', 'gen-sop-037', 'gen-sop-039', 'gen-sop-047', 'gen-sop-049',
    'gen-sop-057', 'gen-sop-059', 'gen-sop-067', 'gen-sop-069', 'gen-sop-077',
    'gen-sop-079', 'gen-sop-087', 'gen-sop-089', 'gen-sop-097', 'gen-sop-099'
]
assert len(sop_ids) == 20, f"Expected 20 sophisticated samples, got {len(sop_ids)}"

# 5. 20 ordinary legitimate samples
ord_ids = [f"gen-ord-{i:03d}" for i in range(1, 21)]
assert len(ord_ids) == 20, f"Expected 20 ordinary samples, got {len(ord_ids)}"

selected_ids = active_injection_samples + quoted_injection_samples + dif_ids + sop_ids + ord_ids
assert len(selected_ids) == 160, f"Expected 160 total samples, got {len(selected_ids)}"
assert len(set(selected_ids)) == 160, "Duplicate IDs found!"

out_path = Path("data/evaluation/phase5_regression_160.jsonl")
out_path.parent.mkdir(parents=True, exist_ok=True)

with open(out_path, "w", encoding="utf-8") as f:
    for sid in selected_ids:
        row = all_samples[sid]
        # Ensure sample_id is set
        if "sample_id" not in row:
            row["sample_id"] = sid
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"Successfully generated {out_path} with {len(selected_ids)} samples.")
print(f"  Active injection: {len(active_injection_samples)} (includes 5 Chinese)")
print(f"  Quoted injection: {len(quoted_injection_samples)}")
print(f"  Difficult legitimate: {len(dif_ids)}")
print(f"  Sophisticated phishing: {len(sop_ids)}")
print(f"  Ordinary legitimate: {len(ord_ids)}")
