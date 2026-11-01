import hashlib
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROTECTED_FILES = {
    "Production M4": ("src/core/inference.py", "aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506"),
    "Frozen A1": ("src/core/inference_m4_v2.py", "fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37"),
    "Clean FAISS Index": ("results/rag_index_clean/index.faiss", "d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc"),
    "A1 Gen Benchmark": ("data/evaluation/a1_generalization_v1.jsonl", "ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336"),
    "A1 Gen Preds": ("results/a1_generalization_v1/predictions.jsonl", "7b1645eeae682bfbdaffb28dce7930ec71b2ccbf3cc519417ed99c4b9459589e"),
    "M4 Ablation Preds": ("results/m4_ablation_v1/predictions.jsonl", "4a0cb0afdda10d22420d39a2b9fff754287f9a054a9c32485a517a70a003b449"),
    "Phase 5 Regression Suite": ("data/evaluation/phase5_regression_160.jsonl", "325bf42f244120667aa00051ed0e2086b02645958c138699cd3bd32d615fc606"),
    "Phase 5 Predictions": ("results/phase5_a1_sanitizer_latency/predictions.jsonl", "cf569e133a1aa3a39f8ed2b725ef5e34ce8c140be630b6b2851115d7db15847d"),
    "Phase 6 Domain Challenge": ("data/evaluation/phase6_domain_challenge.jsonl", "02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7"),
}

print(f"{'Component':25s} | {'Path':55s} | {'Status':8s}")
print("-" * 95)

all_ok = True
for name, (path_str, expected_hash) in PROTECTED_FILES.items():
    p = Path(path_str)
    if not p.exists():
        print(f"{name:25s} | {path_str:55s} | MISSING")
        all_ok = False
        continue
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    actual_hash = h.hexdigest()
    if actual_hash == expected_hash:
        print(f"{name:25s} | {path_str:55s} | INVARIANT")
    else:
        print(f"{name:25s} | {path_str:55s} | MISMATCH")
        print(f"  Expected: {expected_hash}")
        print(f"  Actual:   {actual_hash}")
        all_ok = False

if all_ok:
    print("\nALL PROTECTED HISTORICAL FILES & DATASETS ARE CRYPTOGRAPHICALLY INVARIANT.")
else:
    print("\nPROTECTED FILE AUDIT FAILED.")
    sys.exit(1)
