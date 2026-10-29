import json
from pathlib import Path

diag_path = Path("data/diagnostic_suite.json")
with open(diag_path, "r", encoding="utf-8") as f:
    diag_data = json.load(f)

print(f"Total diagnostic examples: {len(diag_data)}")
labels = [d["true_label"] for d in diag_data]
print(f"Phishing count (1): {labels.count(1)}")
print(f"Legitimate count (0): {labels.count(0)}")

categories = {}
for d in diag_data:
    cat = d["category"]
    categories[cat] = categories.get(cat, 0) + 1
print("Categories:", json.dumps(categories, indent=2))

# Check data leakage against train.jsonl and RAG metadata.jsonl
train_path = Path("data/splits/review_seed42/train.jsonl")
train_texts = set()
if train_path.exists():
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                train_texts.add(json.loads(line).get("text", "").strip())
print(f"Loaded {len(train_texts)} train texts.")

rag_path = Path("results/rag_index/metadata.jsonl")
rag_texts = set()
if rag_path.exists():
    with open(rag_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rag_texts.add(json.loads(line).get("text", "").strip())
print(f"Loaded {len(rag_texts)} RAG metadata texts.")

exact_train_overlaps = []
exact_rag_overlaps = []
for d in diag_data:
    full_t = f"Subject: {d.get('subject', '')}\nFrom: {d.get('sender', '')}\n\n{d['body']}".strip()
    body_t = d["body"].strip()
    if full_t in train_texts or body_t in train_texts:
        exact_train_overlaps.append(d["id"])
    if full_t in rag_texts or body_t in rag_texts:
        exact_rag_overlaps.append(d["id"])

print(f"Exact overlaps with train.jsonl: {len(exact_train_overlaps)} -> {exact_train_overlaps}")
print(f"Exact overlaps with RAG metadata: {len(exact_rag_overlaps)} -> {exact_rag_overlaps}")

# Recalculate metrics for both evaluation files
for fname in ["scratch/baseline_diagnostic_results_qwen2.5_0.5b.json", "scratch/baseline_diagnostic_results_qwen3.5_4b.json"]:
    fpath = Path(fname)
    if not fpath.exists():
        print(f"File {fname} does not exist.")
        continue
    print("\n" + "="*80)
    print(f"RECALCULATING METRICS FOR: {fname}")
    print("="*80)
    with open(fpath, "r", encoding="utf-8") as f:
        res = json.load(f)
    
    # Check predictions structure
    preds = res.get("predictions", {})
    methods = ["M1", "M2", "M3", "M4"]
    
    for m in methods:
        m_preds = preds.get(m, [])
        print(f"\n--- Method: {m} (Evaluated samples: {len(m_preds)}) ---")
        if len(m_preds) != len(diag_data):
            print(f"WARNING: Sample count mismatch! {len(m_preds)} vs {len(diag_data)}")
        
        tp = fp = tn = fn = errors = 0
        cat_stats = {}
        for p, d in zip(m_preds, diag_data):
            assert p["id"] == d["id"], f"ID mismatch {p['id']} vs {d['id']}"
            true_label = d["true_label"] # 1: phish, 0: legit
            cat = d["category"]
            if cat not in cat_stats:
                cat_stats[cat] = {"correct": 0, "total": 0}
            cat_stats[cat]["total"] += 1
            
            # Prediction
            # Note: in prediction record: p["is_phishing"] is bool, p["valid"] is bool
            if not p.get("valid", True):
                errors += 1
            
            pred_is_phish = p.get("is_phishing", False)
            pred_label = 1 if pred_is_phish else 0
            
            if true_label == 1 and pred_label == 1:
                tp += 1
                cat_stats[cat]["correct"] += 1
            elif true_label == 0 and pred_label == 1:
                fp += 1
            elif true_label == 0 and pred_label == 0:
                tn += 1
                cat_stats[cat]["correct"] += 1
            elif true_label == 1 and pred_label == 0:
                fn += 1
        
        acc = (tp + tn) / len(diag_data) if len(diag_data) else 0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        print(f"  Confusion Matrix : TP={tp} | FP={fp} | TN={tn} | FN={fn}")
        print(f"  Accuracy         : {acc*100:.2f}%")
        print(f"  Precision        : {prec*100:.2f}%")
        print(f"  Recall           : {rec*100:.2f}%")
        print(f"  F1-Score         : {f1*100:.2f}%")
        print(f"  FPR (False Alarm): {fpr*100:.2f}%")
        print(f"  FNR (Missed Phish): {fnr*100:.2f}%")
        print(f"  Errors / Invalid : {errors}")
        print("  Category Performance:")
        for cat, s in cat_stats.items():
            pct = s["correct"] / s["total"] * 100 if s["total"] else 0
            print(f"    - {cat:38}: {s['correct']}/{s['total']} ({pct:.1f}%)")
