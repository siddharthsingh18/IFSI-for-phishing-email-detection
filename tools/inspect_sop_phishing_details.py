import json
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

with open("results/phase5_a1_sanitizer_latency/predictions.jsonl", "r", encoding="utf-8") as f:
    preds = [json.loads(line) for line in f]

sop_a1 = {p["sample_id"]: p for p in preds if p["config_id"] == "A1" and p["sample_id"].startswith("gen-sop-")}
sop_opt = {p["sample_id"]: p for p in preds if p["config_id"] == "A1-Opt" and p["sample_id"].startswith("gen-sop-")}

print(f"Total sophisticated phishing samples: {len(sop_a1)}")
for sid in sorted(sop_a1.keys()):
    r1 = sop_a1[sid]
    r2 = sop_opt[sid]
    print(f"Sample: {sid}")
    print(f"  Sender: {r1.get('sender')}")
    print(f"  Subject: {r1.get('subject')}")
    print(f"  A1 Pred: {r1.get('is_phishing')} | Action: {r1.get('security_action')}")
    print(f"  Opt Pred: {r2.get('is_phishing')} | Action: {r2.get('security_action')}")
    print(f"  A1 Reasons: {r1.get('reasons')}")
    print(f"  Opt Reasons: {r2.get('reasons')}")
    print("-" * 60)
