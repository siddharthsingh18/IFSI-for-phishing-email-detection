import json
from collections import defaultdict

with open('data/evaluation/live_benchmark_v2.jsonl', 'r', encoding='utf-8') as f:
    v2_samples = {json.loads(line)['id']: json.loads(line) for line in f if line.strip()}

with open('data/evaluation/heldout_benchmark_v1.jsonl', 'r', encoding='utf-8') as f:
    heldout_samples = {json.loads(line)['id']: json.loads(line) for line in f if line.strip()}

all_samples = {**v2_samples, **heldout_samples}
inj_samples = {sid: s for sid, s in all_samples.items() if s.get('has_prompt_injection')}

preds_by_config = defaultdict(dict)
with open('results/m4_ablation_v1/predictions.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        if r['sample_id'] in inj_samples:
            preds_by_config[r['config_id']][r['sample_id']] = r

print(f"Total Injection Samples: {len(inj_samples)}")

active_sids = [sid for sid, s in inj_samples.items() if s.get('is_phishing')]
quoted_sids = [sid for sid, s in inj_samples.items() if not s.get('is_phishing')]

print(f"Active injection samples (GT Phishing): {len(active_sids)}")
print(f"Quoted injection samples (GT Genuine): {len(quoted_sids)}")

print("\n--- QUOTED INJECTION BREAKDOWN BY CONFIG ---")
for cid in ["A0", "ISO-4", "A1", "A2", "A3", "A4", "ISO-1", "ISO-2", "ISO-3"]:
    fails = []
    blocks = []
    phish_pred = []
    for sid in quoted_sids:
        p = preds_by_config[cid][sid]
        act = p.get('security_action')
        ph = p.get('is_phishing')
        q = p.get('quoted_prompt_injection')
        a = p.get('active_prompt_injection')
        
        if ph or act == 'block' or not q:
            fails.append((sid, ph, act, q, a))
        if act == 'block':
            blocks.append(sid)
        if ph:
            phish_pred.append(sid)
    print(f"[{cid}] Quoted Failures: {len(fails)}/25 | Flagged Phish: {len(phish_pred)} | Security Action Block: {len(blocks)}")
    if fails and cid in ["A0", "ISO-4", "A1", "A4"]:
        for sid, ph, act, q, a in fails:
            print(f"   {sid}: phish={ph}, action={act}, quoted={q}, active={a}")

