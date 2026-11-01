import os

path = "results/phase6_domain_evidence/predictions.jsonl"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = sum(1 for line in f if line.strip())
    print(f"Total lines in predictions.jsonl: {lines}")
else:
    print("File does not exist yet.")

