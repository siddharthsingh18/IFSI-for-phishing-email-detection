import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("results/phase6_domain_evidence/predictions.jsonl", "r", encoding="utf-8") as f:
    preds = [json.loads(line) for line in f if line.strip()]

by_config = {}
for p in preds:
    cfg = p["config_id"]
    sid = p["sample_id"]
    if cfg not in by_config:
        by_config[cfg] = {}
    by_config[cfg][sid] = p

print("--- Config B False Positives (Ground Truth: Legitimate, Pred: Phishing) ---")
count = 0
for sid, p in by_config.get("B", {}).items():
    if not p["ground_truth_is_phishing"] and p["is_phishing"]:
        count += 1
        print(f"\n[{count}] Sample ID: {sid} | Dataset: {p.get('dataset')} | Category: {p.get('category')} | Subcategory: {p.get('subcategory')}")
        print(f"  Sender: {p.get('sender')}")
        print(f"  Subject: {p.get('subject')}")
        print(f"  Reasons: {p.get('reasons')}")
        obs = p.get("domain_telemetry", {}).get("observations", []) if p.get("domain_telemetry") else []
        print(f"  Domain Observations: {obs}")

print("\n--- Invariance Divergence Sample: p6-sop-016 ---")
p_a = by_config.get("A", {}).get("p6-sop-016")
p_c = by_config.get("C", {}).get("p6-sop-016")
p_b = by_config.get("B", {}).get("p6-sop-016")
if p_a and p_c:
    print(f"Subject: {p_a.get('subject')}")
    print(f"Sender: {p_a.get('sender')}")
    print(f"Pred A: is_phish={p_a.get('is_phishing')}, reasons={p_a.get('reasons')}")
    print(f"Pred C: is_phish={p_c.get('is_phishing')}, reasons={p_c.get('reasons')}")
    if p_b:
        print(f"Pred B: is_phish={p_b.get('is_phishing')}, reasons={p_b.get('reasons')}")

