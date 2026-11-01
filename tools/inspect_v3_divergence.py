import json
from pathlib import Path

p6_preds = {r["sample_id"]: r for r in [json.loads(x) for x in open("results/phase6_domain_evidence/predictions.jsonl", encoding="utf-8")] if r.get("config_id") == "B"}
p7_preds = {r["sample_id"]: r for r in [json.loads(x) for x in open("results/phase7_domain_precision/predictions.jsonl", encoding="utf-8")] if r.get("config_id") == "B"}

samples = ["gen-dif-004", "gen-inj-051", "p6-leg-007", "gen-ord-010", "p6-leg-015"]

for sid in samples:
    r6 = p6_preds.get(sid)
    r7 = p7_preds.get(sid)
    print(f"\n=================== SAMPLE {sid} ===================")
    if r6:
        print(f"Phase 6 Config B: is_phish={r6.get('is_phishing')} | action={r6.get('security_action')}")
        print("P6 Domain Telemetry:", r6.get("domain_telemetry"))
        print("P6 Reasons:", r6.get("reasons"))
    else:
        print("Phase 6 Config B: not present")
    if r7:
        print(f"Phase 7 Config B: is_phish={r7.get('is_phishing')} | action={r7.get('security_action')}")
        print("P7 Domain Telemetry:", r7.get("domain_telemetry"))
        print("P7 Reasons:", r7.get("reasons"))
    else:
        print("Phase 7 Config B: not present")

