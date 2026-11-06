"""Phase 9.1 Candidate Freeze and Reproducibility Manifest Generator.

Audits and records SHA-256 hashes of:
1. All candidate engine implementations, prompts, sanitizers, and analyzers.
2. Protected baseline files.
3. Historical evaluation datasets.
4. Historical prediction and metric artifacts.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parents[1]
PHASE9_DIR = BASE_DIR / "results" / "phase9"
PHASE9_DIR.mkdir(parents=True, exist_ok=True)

PROTECTED_BASELINES = {
    "Production M4 (A0)": (BASE_DIR / "src" / "core" / "inference.py", "aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506"),
    "Frozen A1": (BASE_DIR / "src" / "core" / "inference_m4_v2.py", "fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37"),
    "Clean FAISS Index": (BASE_DIR / "results" / "rag_index_clean" / "index.faiss", "d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc"),
    "Clean FAISS Metadata": (BASE_DIR / "results" / "rag_index_clean" / "metadata.json", "4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece"),
    "Phase 5 Sanitizer V2": (BASE_DIR / "src" / "experiments" / "phase5_a1_optimization" / "sanitizer_v2.py", "b51f938ca3a3b4e2b9f4212d4178b58cd47c3f8b4a48a0ba9a0539be4759aa55"),
    "Phase 6 Domain Analyzer V2": (BASE_DIR / "src" / "experiments" / "phase6_domain_evidence" / "domain_analyzer_v2.py", "e27aefb062350e758840aedd4ecb5eb29e43ae19b61f228a3c864aa3df59fc44"),
    "Phase 6 Engine V3": (BASE_DIR / "src" / "experiments" / "phase6_domain_evidence" / "engine_v3.py", "dbe5150dc7365b6a560b09f9056129fc24d50e0ebfa13c53719c6336263ae8a8"),
    "Phase 7 Domain Analyzer V3": (BASE_DIR / "src" / "experiments" / "phase7_domain_precision" / "domain_analyzer_v3.py", "7abde00e3795c7e02504d60ad1f631e101eeefb7b9566c70b73bc02b25f32525"),
    "Phase 7 Engine V4": (BASE_DIR / "src" / "experiments" / "phase7_domain_precision" / "engine_v4.py", "b3c6e9b86d664fc911c82f80e81bff7686cbd2032352fd9326b5e0c40f689b01"),
    "Phase 5 Regression 160": (BASE_DIR / "data" / "evaluation" / "phase5_regression_160.jsonl", "325bf42f244120667aa00051ed0e2086b02645958c138699cd3bd32d615fc606"),
    "Phase 6 Domain Challenge": (BASE_DIR / "data" / "evaluation" / "phase6_domain_challenge.jsonl", "02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7"),
    "Phase 7 Precision Challenge": (BASE_DIR / "data" / "evaluation" / "phase7_precision_challenge.jsonl", "a6ea7aa12d5bc997939d9cd8c721b728fc6fc22cc2a6aab0ef38912f7fb71c1c"),
}

CANDIDATE_COMPONENTS = {
    "Production M4 Engine": BASE_DIR / "src" / "core" / "inference.py",
    "Frozen A1 Engine": BASE_DIR / "src" / "core" / "inference_m4_v2.py",
    "Sanitizer V1": BASE_DIR / "src" / "core" / "sanitizer.py",
    "Domain Analyzer V1": BASE_DIR / "src" / "core" / "domain_analyzer.py",
    "Balanced Retriever": BASE_DIR / "src" / "core" / "balanced_retriever.py",
    "Model Config": BASE_DIR / "src" / "core" / "model_config.py",
    "Model Loaders": BASE_DIR / "src" / "core" / "models.py",
    "UI Utils Source of Truth": BASE_DIR / "src" / "ui_utils.py",
    "Phase 5 A1-Opt Engine V2": BASE_DIR / "src" / "experiments" / "phase5_a1_optimization" / "engine_v2.py",
    "Phase 5 Sanitizer V2": BASE_DIR / "src" / "experiments" / "phase5_a1_optimization" / "sanitizer_v2.py",
    "Phase 5 Prompts V2": BASE_DIR / "src" / "experiments" / "phase5_a1_optimization" / "prompts_v2.py",
    "Phase 6 Engine V3": BASE_DIR / "src" / "experiments" / "phase6_domain_evidence" / "engine_v3.py",
    "Phase 6 Domain Analyzer V2": BASE_DIR / "src" / "experiments" / "phase6_domain_evidence" / "domain_analyzer_v2.py",
    "Phase 6 Prompts V3": BASE_DIR / "src" / "experiments" / "phase6_domain_evidence" / "prompts_v3.py",
    "Phase 7 Engine V4": BASE_DIR / "src" / "experiments" / "phase7_domain_precision" / "engine_v4.py",
    "Phase 7 Domain Analyzer V3": BASE_DIR / "src" / "experiments" / "phase7_domain_precision" / "domain_analyzer_v3.py",
}

DATASETS = {
    "Phase 4 Live Benchmark V2": BASE_DIR / "data" / "evaluation" / "live_benchmark_v2.jsonl",
    "Phase 4 Held-Out Benchmark V1": BASE_DIR / "data" / "evaluation" / "heldout_benchmark_v1.jsonl",
    "A1 Generalization Validation V1": BASE_DIR / "data" / "evaluation" / "a1_generalization_v1.jsonl",
    "Phase 5 Regression 160": BASE_DIR / "data" / "evaluation" / "phase5_regression_160.jsonl",
    "Phase 6 Domain Challenge 80": BASE_DIR / "data" / "evaluation" / "phase6_domain_challenge.jsonl",
    "Phase 7 Precision Challenge 80": BASE_DIR / "data" / "evaluation" / "phase7_precision_challenge.jsonl",
}

EXPERIMENT_ARTIFACTS = {
    "Phase 4 Ablation Predictions": BASE_DIR / "results" / "m4_ablation_v1" / "predictions.jsonl",
    "Phase 4 Ablation Metrics": BASE_DIR / "results" / "m4_ablation_v1" / "metrics.json",
    "Phase 4 Ablation Verified Metrics": BASE_DIR / "results" / "m4_ablation_v1" / "independently_verified_metrics.json",
    "A1 Generalization Predictions": BASE_DIR / "results" / "a1_generalization_v1" / "predictions.jsonl",
    "A1 Generalization Metrics": BASE_DIR / "results" / "a1_generalization_v1" / "metrics.json",
    "Phase 5 Optimization Predictions": BASE_DIR / "results" / "phase5_a1_sanitizer_latency" / "predictions.jsonl",
    "Phase 5 Optimization Regression Metrics": BASE_DIR / "results" / "phase5_a1_sanitizer_latency" / "regression_metrics.json",
    "Phase 5 Optimization Independent Metrics": BASE_DIR / "results" / "phase5_a1_sanitizer_latency" / "independent_metrics.json",
    "Phase 6 Domain Evidence Predictions": BASE_DIR / "results" / "phase6_domain_evidence" / "predictions.jsonl",
    "Phase 6 Domain Evidence Independent Metrics": BASE_DIR / "results" / "phase6_domain_evidence" / "independent_metrics.json",
    "Phase 7 Domain Precision Predictions": BASE_DIR / "results" / "phase7_domain_precision" / "predictions.jsonl",
    "Phase 7 Domain Precision Independent Metrics": BASE_DIR / "results" / "phase7_domain_precision" / "independent_metrics.json",
    "Phase 7 Final Audit Summary": BASE_DIR / "results" / "phase7_final_audit" / "audit_summary.json",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def count_lines(path: Path) -> int:
    count = 0
    with open(path, "rb") as f:
        for _ in f:
            count += 1
    return count


def main():
    print("=" * 70)
    print("PHASE 9.1: IMMUTABLE CANDIDATE AUDIT & REPRODUCIBILITY MANIFEST")
    print("=" * 70)

    print("\n1. PROTECTED BASELINE INVARIANTS:")
    all_ok = True
    for name, (path, exp) in PROTECTED_BASELINES.items():
        if not path.exists():
            print(f"  [MISSING] {name}: {path}")
            all_ok = False
            continue
        act = sha256_file(path)
        match = (act == exp)
        if not match:
            all_ok = False
        print(f"  [{'MATCH' if match else 'FAIL'}] {name}: {act}")

    print("\n2. CANDIDATE IMPLEMENTATION SOURCE CODE:")
    for name, path in CANDIDATE_COMPONENTS.items():
        if not path.exists():
            print(f"  [MISSING] {name}: {path}")
            continue
        h = sha256_file(path)
        size = path.stat().st_size
        print(f"  {name:30s} | {size:7d} B | {h}")

    print("\n3. EVALUATION DATASETS:")
    for name, path in DATASETS.items():
        if not path.exists():
            print(f"  [MISSING] {name}: {path}")
            continue
        h = sha256_file(path)
        size = path.stat().st_size
        n_samples = count_lines(path)
        print(f"  {name:32s} | N={n_samples:4d} | {size:8d} B | {h}")

    print("\n4. HISTORICAL EXPERIMENT ARTIFACTS:")
    for name, path in EXPERIMENT_ARTIFACTS.items():
        if not path.exists():
            print(f"  [MISSING] {name}: {path}")
            continue
        h = sha256_file(path)
        size = path.stat().st_size
        lines = count_lines(path) if path.suffix == ".jsonl" else 0
        extra = f"lines={lines:4d}" if lines else "         "
        print(f"  {name:42s} | {size:8d} B | {extra} | {h}")

    print("\nVerification status:", "ALL PROTECTED INVARIANTS PASS" if all_ok else "INVARIANT MISMATCH")


if __name__ == "__main__":
    main()
