import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

preds = []
with open("results/m4_ablation_v1/predictions.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        preds.append(json.loads(line))

by_sample = {}
for p in preds:
    sid = p["sample_id"]
    cfg = p["config_id"]
    if sid not in by_sample:
        by_sample[sid] = {}
    by_sample[sid][cfg] = p

print("Samples where A1 was Phishing=True (TP) and A2 was Phishing=False (FN):")
count = 0
for sid, cfgs in by_sample.items():
    p1 = cfgs.get("A1")
    p2 = cfgs.get("A2")
    if not p1 or not p2:
        continue
    gt = p1["ground_truth_is_phishing"]
    pred1 = p1["is_phishing"]
    pred2 = p2["is_phishing"]
    cat = p1["category"]
    
    if gt == True and pred1 == True and pred2 == False:
        count += 1
        print(f"\n[{count}] Sample ID: {sid} | Cat: {cat} | Diff: {p1.get('difficulty')}")
        print(f"  Sender: {p1.get('sender')}")
        print(f"  Subject: {p1.get('subject')}")
        print(f"  A1 Reasons: {p1.get('reasons')}")
        print(f"  A2 Reasons: {p2.get('reasons')}")

print(f"\nTotal A1 TP -> A2 FN: {count}")

print("\nSamples where A2 was Phishing=True (TP) and A1 was Phishing=False (FN):")
count2 = 0
for sid, cfgs in by_sample.items():
    p1 = cfgs.get("A1")
    p2 = cfgs.get("A2")
    if not p1 or not p2:
        continue
    gt = p1["ground_truth_is_phishing"]
    pred1 = p1["is_phishing"]
    pred2 = p2["is_phishing"]
    cat = p1["category"]
    
    if gt == True and pred1 == False and pred2 == True:
        count2 += 1
        print(f"\n[{count2}] Sample ID: {sid} | Cat: {cat}")
        print(f"  Sender: {p1.get('sender')}")
        print(f"  Subject: {p1.get('subject')}")
        print(f"  A1 Reasons: {p1.get('reasons')}")
        print(f"  A2 Reasons: {p2.get('reasons')}")

print(f"\nTotal A2 TP -> A1 FN: {count2}")
