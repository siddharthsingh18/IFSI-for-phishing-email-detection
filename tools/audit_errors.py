import json
from pathlib import Path

with open("results/m4_experiment_v1/predictions.jsonl", "r", encoding="utf-8") as f:
    preds = [json.loads(line) for line in f if line.strip()]

print(f"Total predictions recorded: {len(preds)}")

for ds in ["live_benchmark_v2", "heldout_benchmark_v1"]:
    print("=" * 80)
    print(f"DATASET: {ds}")
    print("=" * 80)
    for model in ["M4_Baseline", "M4_Experimental"]:
        recs = [r for r in preds if r.get("dataset_name") == ds and r["architecture"] == model]
        fps = [r for r in recs if r["ground_truth_label"] == 0 and r["predicted_phishing_label"] == 1]
        fns = [r for r in recs if r["ground_truth_label"] == 1 and r["predicted_phishing_label"] == 0]
        missed_inj = [r for r in recs if r.get("ground_truth_injection") and not r.get("has_prompt_injection")]
        false_inj = [r for r in recs if not r.get("ground_truth_injection") and r.get("has_prompt_injection")]
        print(f"\n--- Model: {model} (Total evaluated: {len(recs)}) ---")
        print(f"FP ({len(fps)}): {[r['email_id'] for r in fps]}")
        print(f"FN ({len(fns)}): {[r['email_id'] for r in fns]}")
        print(f"Missed Injections ({len(missed_inj)}): {[r['email_id'] for r in missed_inj]}")
        print(f"False Injections ({len(false_inj)}): {[r['email_id'] for r in false_inj]}")
        
        # Check security action distributions
        actions = {}
        for r in recs:
            act = r.get("security_action", "allow")
            actions[act] = actions.get(act, 0) + 1
        print(f"Security Actions: {actions}")

