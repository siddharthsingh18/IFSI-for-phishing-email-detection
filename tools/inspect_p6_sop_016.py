import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("results/phase6_domain_evidence/predictions.jsonl", "r", encoding="utf-8") as f:
    preds = [json.loads(line) for line in f if line.strip()]

preds_a = {p["sample_id"]: p for p in preds if p["config_id"] == "A"}
preds_b = {p["sample_id"]: p for p in preds if p["config_id"] == "B"}
preds_c = {p["sample_id"]: p for p in preds if p["config_id"] == "C"}

sid = "p6-sop-016"
pa = preds_a.get(sid, {})
pb = preds_b.get(sid, {})
pc = preds_c.get(sid, {})

print("=" * 80)
print(f"SAMPLE {sid} PREDICTION COMPARISON")
print("=" * 80)
print(f"Subject: {pa.get('subject')}")
print(f"Sender:  {pa.get('sender')}")
print(f"Ground Truth is_phishing: {pa.get('ground_truth_is_phishing')}")

print("\n--- CONFIG A ---")
print(f"Timestamp: {pa.get('timestamp')}")
print(f"is_phishing: {pa.get('is_phishing')}")
print(f"security_action: {pa.get('security_action')}")
print(f"confidence: {pa.get('confidence')}")
print(f"reasons: {pa.get('reasons')}")
print(f"retrieved_exemplar_ids: {pa.get('retrieved_exemplar_ids')}")
print(f"stage1_latency: {pa.get('stage1_latency_ms')} ms, stage2_latency: {pa.get('stage2_latency_ms')} ms")

print("\n--- CONFIG C ---")
print(f"Timestamp: {pc.get('timestamp')}")
print(f"is_phishing: {pc.get('is_phishing')}")
print(f"security_action: {pc.get('security_action')}")
print(f"confidence: {pc.get('confidence')}")
print(f"reasons: {pc.get('reasons')}")
print(f"retrieved_exemplar_ids: {pc.get('retrieved_exemplar_ids')}")
print(f"stage1_latency: {pc.get('stage1_latency_ms')} ms, stage2_latency: {pc.get('stage2_latency_ms')} ms")

print("\n--- CONFIG B ---")
print(f"Timestamp: {pb.get('timestamp')}")
print(f"is_phishing: {pb.get('is_phishing')}")
print(f"security_action: {pb.get('security_action')}")
print(f"confidence: {pb.get('confidence')}")
print(f"reasons: {pb.get('reasons')}")
print(f"retrieved_exemplar_ids: {pb.get('retrieved_exemplar_ids')}")

