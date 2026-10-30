import sys
import json
sys.path.insert(0, "src")
from core.inference_m4_v2 import classify_email_m4_v2

with open("data/evaluation/live_benchmark_v2.jsonl", "r", encoding="utf-8") as f:
    v2_data = {json.loads(line)["id"]: json.loads(line) for line in f if line.strip()}

check_ids = ["v2-sop-16", "v2-dif-14", "v2-dif-15", "v2-inj-20", "v2-inj-22", "v2-inj-29"]

for cid in check_ids:
    e = v2_data[cid]
    fmt = f"Subject: {e['subject']}\nFrom: {e['sender']}\n\n{e['body']}"
    res = classify_email_m4_v2(fmt, subject=e["subject"], sender=e["sender"])
    print(f"[{cid}] GT Phish={e['is_phishing']} Inj={e.get('has_prompt_injection')}")
    print(f"  Pred: Phish={res['is_phishing']}, ActiveInj={res['active_prompt_injection']}, QuotedInj={res['quoted_prompt_injection']}, Action={res['security_action']}")
    print(f"  Reasons: {res['reasons']}")

