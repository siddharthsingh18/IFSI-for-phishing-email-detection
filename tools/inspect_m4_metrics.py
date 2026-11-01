import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("results/m4_ablation_v1/metrics.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print(f"{'Config':8s} | {'Acc':8s} | {'Prec':8s} | {'Recall':8s} | {'F1':8s} | {'FPR':8s} | {'FNR':8s} | {'TP':5s} | {'TN':5s} | {'FP':5s} | {'FN':5s}")
print("-" * 85)

for cfg, data in d["configurations"].items():
    m = data["combined_250"]
    cm = m["confusion_matrix"]
    print(f"{cfg:8s} | {m['phishing_accuracy']:8.4f} | {m['phishing_precision']:8.4f} | {m['phishing_recall']:8.4f} | {m['phishing_f1']:8.4f} | {m['false_positive_rate']:8.4f} | {m['false_negative_rate']:8.4f} | {cm['tp']:5d} | {cm['tn']:5d} | {cm['fp']:5d} | {cm['fn']:5d}")

print("\n--- Domain Analysis Direct Comparison (A1 vs A2) ---")
a1 = d["configurations"]["A1"]["combined_250"]
a2 = d["configurations"]["A2"]["combined_250"]
print(f"A1 (Domain OFF): Acc={a1['phishing_accuracy']:.4f}, Prec={a1['phishing_precision']:.4f}, Rec={a1['phishing_recall']:.4f}, FPR={a1['false_positive_rate']:.4f}, FP={a1['confusion_matrix']['fp']}, FN={a1['confusion_matrix']['fn']}")
print(f"A2 (Domain ON):  Acc={a2['phishing_accuracy']:.4f}, Prec={a2['phishing_precision']:.4f}, Rec={a2['phishing_recall']:.4f}, FPR={a2['false_positive_rate']:.4f}, FP={a2['confusion_matrix']['fp']}, FN={a2['confusion_matrix']['fn']}")

print("\nCategory breakdown for A1 vs A2:")
for cat in a1["category_accuracy"]:
    acc1 = a1["category_accuracy"][cat]["accuracy"]
    acc2 = a2["category_accuracy"][cat]["accuracy"]
    c1 = a1["category_accuracy"][cat]["correct"]
    c2 = a2["category_accuracy"][cat]["correct"]
    tot = a1["category_accuracy"][cat]["total"]
    print(f"  {cat:25s}: A1 = {acc1:.4f} ({c1}/{tot}) | A2 = {acc2:.4f} ({c2}/{tot}) | Diff = {acc2 - acc1:+.4f}")
