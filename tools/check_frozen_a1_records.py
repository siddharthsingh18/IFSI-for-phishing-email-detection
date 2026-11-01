import json

# Check if all 160 samples have Frozen A1 predictions in historical predictions.jsonl
reg_ids = set()
with open("data/evaluation/phase5_regression_160.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        reg_ids.add(json.loads(line)["sample_id"])

a1_historical = {}
with open("results/a1_generalization_v1/predictions.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        if row.get("config_id") == "A1":
            a1_historical[row["sample_id"]] = row

print(f"Total regression sample IDs: {len(reg_ids)}")
print(f"Total historical A1 records found: {len(a1_historical)}")
matched = [sid for sid in reg_ids if sid in a1_historical]
print(f"Matched regression samples in historical A1: {len(matched)} / {len(reg_ids)}")

