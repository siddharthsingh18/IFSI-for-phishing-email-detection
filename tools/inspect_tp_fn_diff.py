import json

preds_a1 = {}
preds_opt = {}

with open("results/phase5_a1_sanitizer_latency/predictions.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["config_id"] == "A1":
            preds_a1[r["sample_id"]] = r
        elif r["config_id"] == "A1-Opt":
            preds_opt[r["sample_id"]] = r

diffs = []
for sid in preds_a1:
    r1 = preds_a1[sid]
    r2 = preds_opt.get(sid)
    if not r2:
        continue
    
    p1 = r1["is_phishing"]
    p2 = r2["is_phishing"]
    gt = r1["ground_truth_is_phishing"]
    
    if p1 != p2:
        diffs.append((sid, r1["subcategory"], f"A1={p1}", f"Opt={p2}", f"GT={gt}", r1["security_action"], r2["security_action"]))

print(f"Total differences in is_phishing: {len(diffs)}")
for d in diffs:
    print(d)

