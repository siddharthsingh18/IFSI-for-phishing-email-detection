import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "src")

from core.inference_m4_v2 import classify_email_m4_v2

# Load v2 samples
v2_data = {}
with open("data/evaluation/live_benchmark_v2.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            d = json.loads(line)
            v2_data[d["id"]] = d

test_ids = ["v2-inj-01", "v2-inj-17", "v2-sop-30"]

for tid in test_ids:
    e = v2_data[tid]
    print("=" * 80)
    print(f"Testing ID: {tid} ({e['category']} - {e.get('subcategory')})")
    print(f"Ground Truth: Phish={e['is_phishing']}, Inj={e.get('has_prompt_injection')}")
    fmt = f"Subject: {e['subject']}\nFrom: {e['sender']}\n\n{e['body']}"
    res = classify_email_m4_v2(fmt, subject=e["subject"], sender=e["sender"])
    print(f"Result -> Phish: {res['is_phishing']} (Conf: {res['confidence']})")
    print(f"Active Inj: {res['active_prompt_injection']}, Quoted Inj: {res['quoted_prompt_injection']}")
    print(f"Injection Type: {res['injection_type']}")
    print(f"Security Action: {res['security_action']}")
    print("Reasons:")
    for r in res["reasons"]:
        print(f"  {r}")
    print("=" * 80)
