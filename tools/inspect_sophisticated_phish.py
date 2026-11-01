import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

samples = []
with open("data/evaluation/phase5_regression_160.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        if d.get("category") == "sophisticated_phishing":
            samples.append(d)

print(f"Total sophisticated phishing samples in Phase 5 regression: {len(samples)}")
for i, s in enumerate(samples):
    print(f"\n[{i+1}] ID: {s['id']}")
    print(f"  Sender: {s.get('sender')}")
    print(f"  Subject: {s.get('subject')}")
    body = s.get('body', '')
    print(f"  Body (first 200 chars): {body[:200].replace(chr(10), ' ')}")

