import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Load raw email definitions
raw_samples = {}
with open("data/evaluation/phase5_regression_160.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            d = json.loads(line)
            raw_samples[d.get("id") or d.get("sample_id")] = d

with open("data/evaluation/phase6_domain_challenge.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            d = json.loads(line)
            raw_samples[d.get("id") or d.get("sample_id")] = d

# Load Phase 6 predictions
phase6_preds = {}
with open("results/phase6_domain_evidence/predictions.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            d = json.loads(line)
            if d.get("config_id") == "B":
                phase6_preds[d["sample_id"]] = d

target_ids = ["gen-ord-010", "p6-leg-007", "p6-leg-015"]

for sid in target_ids:
    raw = raw_samples.get(sid, {})
    pred = phase6_preds.get(sid, {})

    print("=" * 80)
    print(f"RECONSTRUCTION FOR SAMPLE: {sid}")
    print("=" * 80)
    print(f"1. Subject: {raw.get('subject')}")
    print(f"   Sender: {raw.get('sender')}")
    print(f"   Category: {raw.get('category')} / {raw.get('subcategory')}")
    print(f"   Ground Truth is_phishing: {raw.get('is_phishing')}")
    print("\n   Full Email Body:\n---")
    print(raw.get('body'))
    print("---\n")
    print(f"2. Pred is_phishing: {pred.get('is_phishing')}")
    print(f"   Pred security_action: {pred.get('security_action')}")
    print(f"   Pred confidence: {pred.get('confidence')}")
    print(f"   Pred reasons: {pred.get('reasons')}")
    print(f"   Pred domain telemetry: {json.dumps(pred.get('domain_telemetry'), indent=2)}")

