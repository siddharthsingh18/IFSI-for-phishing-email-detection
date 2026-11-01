import hashlib
from pathlib import Path

FILES = [
    Path("src/core/inference.py"),
    Path("src/core/inference_m4_v2.py"),
    Path("results/rag_index_clean/index.faiss"),
    Path("data/evaluation/a1_generalization_v1.jsonl"),
    Path("results/a1_generalization_v1/predictions.jsonl"),
    Path("results/m4_ablation_v1/predictions.jsonl"),
]

for p in FILES:
    if p.exists():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        print(f"{p}: {h}")
    else:
        print(f"{p}: MISSING")

