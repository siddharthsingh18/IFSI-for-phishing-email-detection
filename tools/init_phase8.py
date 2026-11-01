"""Phase 8.0 Initialization and Baseline Hash Audit Script.

Verifies:
1. Target directories exist.
2. SHA-256 hashes of all protected files before any Phase 8 action.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

# Required Phase 8 directories
PHASE8_DIRS = [
    BASE_DIR / "src" / "experiments" / "phase8_independent_evaluation",
    BASE_DIR / "data" / "evaluation" / "phase8",
    BASE_DIR / "results" / "phase8_independent_evaluation",
]

for d in PHASE8_DIRS:
    d.mkdir(parents=True, exist_ok=True)

PROTECTED_FILES = {
    "Production Baseline M4": BASE_DIR / "src" / "core" / "inference.py",
    "Frozen A1": BASE_DIR / "src" / "core" / "inference_m4_v2.py",
    "Clean FAISS Index": BASE_DIR / "results" / "rag_index_clean" / "index.faiss",
    "Clean FAISS Metadata": BASE_DIR / "results" / "rag_index_clean" / "metadata.json",
    "Phase 5 Sanitizer V2": BASE_DIR / "src" / "experiments" / "phase5_a1_optimization" / "sanitizer_v2.py",
    "Phase 6 Domain Analyzer V2": BASE_DIR / "src" / "experiments" / "phase6_domain_evidence" / "domain_analyzer_v2.py",
    "Phase 6 Engine V3": BASE_DIR / "src" / "experiments" / "phase6_domain_evidence" / "engine_v3.py",
    "Phase 7 Domain Analyzer V3": BASE_DIR / "src" / "experiments" / "phase7_domain_precision" / "domain_analyzer_v3.py",
    "Phase 7 Engine V4": BASE_DIR / "src" / "experiments" / "phase7_domain_precision" / "engine_v4.py",
    "Phase 5 Regression 160": BASE_DIR / "data" / "evaluation" / "phase5_regression_160.jsonl",
    "Phase 6 Domain Challenge": BASE_DIR / "data" / "evaluation" / "phase6_domain_challenge.jsonl",
    "Phase 7 Precision Challenge": BASE_DIR / "data" / "evaluation" / "phase7_precision_challenge.jsonl",
    "Phase 7 Predictions": BASE_DIR / "results" / "phase7_domain_precision" / "predictions.jsonl",
}

EXPECTED_HASHES = {
    "Production Baseline M4": "aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506",
    "Frozen A1": "fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37",
    "Clean FAISS Index": "d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc",
    "Clean FAISS Metadata": "4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece",
    "Phase 5 Sanitizer V2": "b51f938ca3a3b4e2b9f4212d4178b58cd47c3f8b4a48a0ba9a0539be4759aa55",
    "Phase 6 Domain Analyzer V2": "e27aefb062350e758840aedd4ecb5eb29e43ae19b61f228a3c864aa3df59fc44",
    "Phase 6 Engine V3": "dbe5150dc7365b6a560b09f9056129fc24d50e0ebfa13c53719c6336263ae8a8",
    "Phase 5 Regression 160": "325bf42f244120667aa00051ed0e2086b02645958c138699cd3bd32d615fc606",
    "Phase 6 Domain Challenge": "02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7",
    "Phase 7 Precision Challenge": "a6ea7aa12d5bc997939d9cd8c721b728fc6fc22cc2a6aab0ef38912f7fb71c1c",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 60)
    print("PHASE 8.0 PRE-AUDIT & DIRECTORY INITIALIZATION")
    print("=" * 60)
    print("Phase 8 Directories:")
    for d in PHASE8_DIRS:
        print(f"  {d.relative_to(BASE_DIR)}: exists={d.exists()}")

    print("\nProtected Baseline Hashes:")
    all_ok = True
    for name, path in PROTECTED_FILES.items():
        if not path.exists():
            print(f"  MISSING: {name} ({path.relative_to(BASE_DIR)})")
            all_ok = False
            continue
        h = sha256_file(path)
        exp = EXPECTED_HASHES.get(name)
        if exp:
            match = (h == exp)
            status = "MATCH" if match else "MISMATCH"
            if not match:
                all_ok = False
            print(f"  {status}: {name} -> {h[:16]}... (exp: {exp[:16]}...)")
        else:
            print(f"  RECORDED: {name} -> {h}")

    print("\nPre-Audit Integrity Status:", "ALL PROTECTED FILES VERIFIED" if all_ok else "INTEGRITY VIOLATION DETECTED")


if __name__ == "__main__":
    main()

