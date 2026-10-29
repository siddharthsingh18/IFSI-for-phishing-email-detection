"""Generate representative benchmark prediction JSONL files in results/ for dashboard tests."""

from __future__ import annotations

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
results_dir = ROOT_DIR / "results"
data_dir = ROOT_DIR / "data"

test_records = []
test_file = data_dir / "splits" / "test.jsonl"
if test_file.exists():
    with open(test_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                test_records.append(json.loads(line.strip()))

if not test_records:
    print("No test records found!")
    exit(1)

# Generate predictions for each method and condition
for m in ("M1", "M2", "M3", "M4"):
    for c in ("clean", "marked", "unmarked"):
        pred_file = results_dir / f"{m}_{c}_predictions.jsonl"
        rows = []
        for idx, rec in enumerate(test_records):
            eid = rec["id"]
            true_label = int(rec["label"])
            # Generate a few realistic mistakes per method (e.g. 5-10 mistakes)
            # High confidence mistake for indices 1, 5, 10, 15, 20
            is_mistake = (idx in (1, 5, 10, 15, 20, 25, 30, 35))
            if is_mistake:
                pred_label = 0 if true_label == 1 else 1
                confidence = 0.95 - (idx * 0.005)
            else:
                pred_label = true_label
                confidence = 0.92

            rows.append({
                "id": eid,
                "original_id": eid,
                "true_label": true_label,
                "predicted_label": pred_label,
                "confidence": round(confidence, 4),
                "is_valid": True,
            })

        with open(pred_file, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"Wrote {len(rows)} predictions to {pred_file}")

print("Done generating results predictions.")

