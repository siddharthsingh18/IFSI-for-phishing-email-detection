import json
from collections import defaultdict

with open('data/evaluation/live_benchmark_v2.jsonl', 'r', encoding='utf-8') as f:
    v2_samples = {json.loads(line)['id']: json.loads(line) for line in f if line.strip()}

with open('data/evaluation/heldout_benchmark_v1.jsonl', 'r', encoding='utf-8') as f:
    heldout_samples = {json.loads(line)['id']: json.loads(line) for line in f if line.strip()}

all_samples = {**v2_samples, **heldout_samples}

preds_by_sample = defaultdict(dict)
with open('results/m4_ablation_v1/predictions.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        preds_by_sample[r['sample_id']][r['config_id']] = r

# Group errors
error_counts = defaultdict(int)
error_configs = defaultdict(list)
error_types = {}

for sid, src in all_samples.items():
    gt = bool(src.get('label', 0) == 1 or src.get('is_phishing', False))
    for cid in ["A0", "ISO-4", "A1", "A2", "A3", "A4", "ISO-1", "ISO-2", "ISO-3"]:
        p = preds_by_sample[sid][cid]
        pred_p = bool(p['is_phishing'])
        if pred_p != gt:
            error_counts[sid] += 1
            error_configs[sid].append(cid)
            error_types[sid] = "FP" if not gt else "FN"

# Sort by fail frequency
sorted_errors = sorted(error_counts.items(), key=lambda x: -x[1])
print(f"Total Unique Samples with at least 1 Error across any config: {len(sorted_errors)}")

categories = defaultdict(list)
for sid, cnt in sorted_errors:
    src = all_samples[sid]
    etype = error_types[sid]
    cat = src.get('category', 'unknown')
    categories[cat].append((sid, cnt, etype, src.get('subject', ''), error_configs[sid]))

print("\n--- ERROR BREAKDOWN BY CATEGORY ---")
for cat, items in sorted(categories.items()):
    print(f"\nCategory: {cat} ({len(items)} samples with errors):")
    for sid, cnt, etype, subj, cfgs in items[:8]:
        subj_clean = subj.encode('ascii', 'replace').decode('ascii')
        print(f"  [{cnt}/9 configs fail] {sid} ({etype}) | {subj_clean[:45]} | cfgs: {','.join(cfgs)}")

