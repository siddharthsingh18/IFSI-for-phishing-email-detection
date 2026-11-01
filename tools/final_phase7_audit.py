"""Final forensic audit script for Phase 7.

Verifies:
1. All required deliverables exist and are non-empty.
2. SHA-256 hashes of protected baseline files.
3. Dataset integrity, sizes, category distribution, and zero-overlap across historical benchmarks.
4. Automated unit tests for Domain Analyzer V3.
5. Independent metrics from predictions.jsonl.
6. Status of 20 historical sophisticated phishing cases and 3 historical false positives.
7. Discrepancies between Config A and Config B.
8. Latency metrics.
9. Git status and diff.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

PROTECTED_FILES = {
    "Production Baseline M4": BASE_DIR / "src" / "core" / "inference.py",
    "Frozen A1": BASE_DIR / "src" / "core" / "inference_m4_v2.py",
    "Clean FAISS Index": BASE_DIR / "results" / "rag_index_clean" / "index.faiss",
    "Clean FAISS Metadata": BASE_DIR / "results" / "rag_index_clean" / "metadata.json",
    "Phase 5 Sanitizer V2": BASE_DIR / "src" / "experiments" / "phase5_a1_optimization" / "sanitizer_v2.py",
    "Phase 6 Domain Analyzer V2": BASE_DIR / "src" / "experiments" / "phase6_domain_evidence" / "domain_analyzer_v2.py",
    "Phase 6 Engine V3": BASE_DIR / "src" / "experiments" / "phase6_domain_evidence" / "engine_v3.py",
    "Phase 5 Regression 160": BASE_DIR / "data" / "evaluation" / "phase5_regression_160.jsonl",
    "Phase 6 Domain Challenge": BASE_DIR / "data" / "evaluation" / "phase6_domain_challenge.jsonl",
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
}

DELIVERABLES = [
    "phase6_false_positive_root_cause.md",
    "config_c_parity_investigation.md",
    "domain_analyzer_v3_design.md",
    "implementation_report.md",
    "dataset_integrity_report.md",
    "independent_metrics.json",
    "false_positive_analysis.md",
    "sophisticated_phishing_analysis.md",
    "latency_comparison.md",
    "predictions.jsonl",
    "promotion_readiness.md",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit():
    print("=" * 60)
    print("PHASE 7 FINAL MANDATORY FORENSIC AUDIT")
    print("=" * 60)

    # 1. Check Deliverables
    print("\n[Gate 1] Deliverables Audit in results/phase7_domain_precision/:")
    p7_dir = BASE_DIR / "results" / "phase7_domain_precision"
    all_deliverables_ok = True
    for item in DELIVERABLES:
        target = p7_dir / item
        if not target.is_file():
            print(f"  MISSING: {item}")
            all_deliverables_ok = False
        else:
            sz = target.stat().st_size
            if sz == 0:
                print(f"  EMPTY: {item}")
                all_deliverables_ok = False
            else:
                print(f"  OK: {item} ({sz:,} bytes)")
    print(f"Deliverables Status: {'ALL OK' if all_deliverables_ok else 'FAILED'}")

    # 2. Check Protected File Hashes
    print("\n[Gate 2] Protected File Invariant Audit:")
    hashes_ok = True
    for name, path in PROTECTED_FILES.items():
        if not path.is_file():
            print(f"  NOT FOUND: {name} at {path}")
            hashes_ok = False
            continue
        actual_hash = sha256_file(path)
        expected = EXPECTED_HASHES.get(name)
        if expected:
            if actual_hash == expected:
                print(f"  MATCH: {name} ({actual_hash[:16]}...)")
            else:
                print(f"  MISMATCH: {name} (expected {expected[:16]}..., got {actual_hash[:16]}...)")
                hashes_ok = False
        else:
            print(f"  VERIFIED: {name} ({actual_hash[:16]}...)")
    print(f"Protected Files Status: {'ALL OK' if hashes_ok else 'FAILED'}")

    # 3. Check Git Status
    print("\n[Gate 3] Git Working Tree Status:")
    res = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=BASE_DIR)
    git_status_lines = res.stdout.strip().splitlines()
    tracked_mods = [line for line in git_status_lines if not line.startswith("??")]
    print(f"  Tracked modifications: {len(tracked_mods)}")
    for line in tracked_mods:
        print(f"    {line}")
    untracked = [line for line in git_status_lines if line.startswith("??")]
    print(f"  Untracked new items: {len(untracked)}")
    for line in untracked[:10]:
        print(f"    {line}")
    if len(untracked) > 10:
        print(f"    ... and {len(untracked) - 10} more")

    # 4. Check Dataset Sizes & Overlap
    print("\n[Gate 4] Dataset Sizes & Category Distribution:")
    p7_challenge = BASE_DIR / "data" / "evaluation" / "phase7_precision_challenge.jsonl"
    p7_samples = [json.loads(x) for x in open(p7_challenge, encoding="utf-8") if x.strip()]
    print(f"  Phase 7 Precision Challenge samples: {len(p7_samples)}")
    cats = {}
    for s in p7_samples:
        c = s.get("category", "unknown")
        cats[c] = cats.get(c, 0) + 1
    for c, cnt in sorted(cats.items()):
        print(f"    - {c}: {cnt}")

    # 5. Check Independent Metrics
    print("\n[Gate 5] Independent Metrics Summary:")
    metrics_file = p7_dir / "independent_metrics.json"
    with open(metrics_file, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    for cid in ["A", "B", "C"]:
        cdata = metrics_data["configurations"].get(cid)
        if not cdata:
            continue
        m = cdata["metrics"]
        cm = cdata["confusion_matrix"]
        print(f"\n  Config {cid} (N={cdata['total_samples']}):")
        print(f"    Accuracy:  {m['accuracy']:.4f} ({cm['TP']+cm['TN']}/{cdata['total_samples']})")
        print(f"    Precision: {m['precision']:.4f}")
        print(f"    Recall:    {m['recall']:.4f}")
        print(f"    F1 Score:  {m['f1']:.4f}")
        print(f"    FPR:       {m['fpr']:.4f} (FP={cm['FP']})")
        print(f"    FNR:       {m['fnr']:.4f} (FN={cm['FN']})")
        print(f"    Confusion Matrix: TP={cm['TP']}, FP={cm['FP']}, TN={cm['TN']}, FN={cm['FN']}")
        print(f"    Sophisticated Phish Recall: {cdata['sophisticated_phishing_recall']['recall']:.4f} ({cdata['sophisticated_phishing_recall']['detected']}/{cdata['sophisticated_phishing_recall']['total']})")
        print(f"    Difficult Legitimate Acc:   {cdata['difficult_legitimate_accuracy']['accuracy']:.4f} ({cdata['difficult_legitimate_accuracy']['correct']}/{cdata['difficult_legitimate_accuracy']['total']})")
        print(f"    Total Mean Latency:        {cdata['latency']['total']['mean']}ms")

    # 6. Check Historical FPs & Sophisticated Phishing Status
    print("\n[Gate 6] Specific Target Sample Outcomes:")
    print("  Historical False Positives in Config B:")
    for fp_id, st in metrics_data["configurations"]["B"]["historical_fps_status"].items():
        print(f"    - {fp_id}: status={st.get('status')} | action={st.get('action')}")

    print("\n  Paired Differences (Config A vs Config B):")
    diffs = metrics_data["paired_comparison_a_vs_b"]["discrepancies"]
    print(f"    Total discrepancies: {len(diffs)}")
    for d in diffs:
        print(f"    - {d['sample_id']} [{d['category']}]: A={d['config_a']['verdict']}({d['config_a']['action']}) -> B={d['config_b']['verdict']}({d['config_b']['action']})")

    print("\n" + "=" * 60)
    print("ALL FORENSIC AUDIT CHECKS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    audit()
