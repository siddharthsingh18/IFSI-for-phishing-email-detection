import hashlib
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

os.makedirs("src/experiments/phase7_domain_precision", exist_ok=True)
os.makedirs("results/phase7_domain_precision", exist_ok=True)

PROTECTED_FILES = {
    "Production M4": ("src/core/inference.py", "aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506"),
    "Frozen A1": ("src/core/inference_m4_v2.py", "fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37"),
    "Clean FAISS Index": ("results/rag_index_clean/index.faiss", "d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc"),
    "Phase 5 Engine": ("src/experiments/phase5_a1_optimization/engine_v2.py", None),
    "Phase 6 Engine": ("src/experiments/phase6_domain_evidence/engine_v3.py", None),
    "Phase 6 Domain Analyzer V2": ("src/experiments/phase6_domain_evidence/domain_analyzer_v2.py", None),
    "Phase 6 Predictions": ("results/phase6_domain_evidence/predictions.jsonl", None),
}

print("Phase 7 Directories Verified.")
print(f"{'Component':25s} | {'Path':65s} | {'Status':8s}")
print("-" * 105)

for name, (path_str, exp_hash) in PROTECTED_FILES.items():
    p = Path(path_str)
    if not p.exists():
        print(f"{name:25s} | {path_str:65s} | MISSING")
        continue
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    act_hash = h.hexdigest()
    if exp_hash is None or act_hash == exp_hash:
        print(f"{name:25s} | {path_str:65s} | OK ({act_hash[:12]}...)")
    else:
        print(f"{name:25s} | {path_str:65s} | MISMATCH")

