import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from experiments.phase7_domain_precision.engine_v4 import classify_email_phase7

sample_path = "data/evaluation/phase7_precision_challenge.jsonl"
with open(sample_path, "r", encoding="utf-8") as f:
    sample = json.loads(f.readline())

sender = sample.get("sender", "")
subject = sample.get("subject", "")
body = sample.get("body", sample.get("text", ""))
if "From:" in body and "Subject:" in body:
    email_text = body
else:
    email_text = f"From: {sender}\nSubject: {subject}\n\n{body}".strip()

print(f"Testing sample {sample['id']}...")
print("Subject:", subject)
print("Sender:", sender)
print("Email text length:", len(email_text))
print("First 200 chars:\n", email_text[:200])

res = classify_email_phase7(email_text, config_id="B", subject=subject, sender=sender)
print("\n--- Result Config B ---")
print("Verdict:", res["verdict"])
print("Action:", res["security_action"])
print("Is phishing:", res["is_phishing"])
print("Domain telemetry:", res["domain_telemetry"])

