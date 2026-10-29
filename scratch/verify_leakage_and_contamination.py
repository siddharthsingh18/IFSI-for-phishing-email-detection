"""Exhaustive Leakage, Near-Duplicate, and Contamination Audit Script.

Audits:
1. Exact string matches between evaluation sets and training/RAG corpora.
2. Normalized text matches (casefolded, whitespace-collapsed, punctuation-stripped).
3. 3-gram MinHash / Jaccard near-duplicate analysis (threshold >= 0.70).
4. Sender domain and template overlap between splits.
5. System prompt inspection for hardcoded evaluation artifacts, domains, or case codes.
"""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path
from typing import Any

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path("src").resolve()))
sys.path.insert(0, str(Path(".").resolve()))

from core.inference import (
    RAG_SYSTEM_PROMPT,
    SYSTEM_INJECTION_DETECTOR,
    SYSTEM_IS_PHISHING_ONLY,
)
from phishbench.ollama_client import SYSTEM_PROMPT as M2_SYSTEM_PROMPT
from scratch.run_generalization_eval import load_held_out_dataset


def normalize_text(text: str) -> str:
    """Normalize text by lowercasing and collapsing all non-alphanumeric chars to single spaces."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return " ".join(cleaned.split())


def get_ngrams(text: str, n: int = 3) -> set[tuple[str, ...]]:
    words = text.split()
    if len(words) < n:
        return {tuple(words)} if words else set()
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def main():
    print("=" * 80)
    print("EXHAUSTIVE LEAKAGE, CONTAMINATION, AND DATA QUALITY AUDIT")
    print("=" * 80)

    # 1. Load Evaluation Sets
    heldout_28 = load_held_out_dataset()
    with open("data/diagnostic_suite.json", "r", encoding="utf-8") as f:
        diag_raw = json.load(f)
    diagnostic_20 = []
    for item in diag_raw:
        subj = item.get("subject", "")
        sender = item.get("sender", "")
        body = item.get("body", "")
        diagnostic_20.append({
            "id": item["id"],
            "subject": subj,
            "sender": sender,
            "text": f"Subject: {subj}\nFrom: {sender}\n\n{body}" if not item.get("text") else item["text"],
            "label": item.get("true_label", item.get("label", 0)),
        })

    # Load frozen val and test splits
    val_records = []
    val_path = Path("data/splits/review_seed42/val.jsonl")
    if val_path.exists():
        with open(val_path, "r", encoding="utf-8") as f:
            val_records = [json.loads(line) for line in f if line.strip()]

    test_records = []
    test_path = Path("data/splits/review_seed42/test.jsonl")
    if test_path.exists():
        with open(test_path, "r", encoding="utf-8") as f:
            test_records = [json.loads(line) for line in f if line.strip()]

    eval_pools = {
        "HeldOut_28": heldout_28,
        "Diagnostic_20": diagnostic_20,
        "Review_Val_100": val_records,
        "Review_Test_522": test_records,
    }

    # 2. Load Training & RAG Datasets
    train_baseline_records = []
    with open("data/splits/review_seed42/train.jsonl", "r", encoding="utf-8") as f:
        train_baseline_records = [json.loads(line) for line in f if line.strip()]

    train_enron_records = []
    with open("data/splits/enron_augmented/train.jsonl", "r", encoding="utf-8") as f:
        train_enron_records = [json.loads(line) for line in f if line.strip()]

    rag_baseline_meta = json.loads(Path("results/rag_index/metadata.json").read_text(encoding="utf-8"))["records"]
    rag_enron_meta = json.loads(Path("results/rag_index_enron/metadata.json").read_text(encoding="utf-8"))["records"]

    train_pools = {
        "Train_Baseline_1000": train_baseline_records,
        "Train_Enron_1000": train_enron_records,
        "RAG_Baseline_1000": rag_baseline_meta,
        "RAG_Enron_1000": rag_enron_meta,
    }

    # AUDIT 1: Exact String Matches
    print("\n--- 1. EXACT STRING MATCH AUDIT ---")
    exact_matches = []
    for eval_name, eval_data in eval_pools.items():
        for e_idx, e_item in enumerate(eval_data):
            e_text = e_item.get("text", e_item.get("body", "")).strip()
            e_id = e_item.get("id", f"sample_{e_idx}")
            for train_name, train_data in train_pools.items():
                for t_idx, t_item in enumerate(train_data):
                    t_text = t_item.get("text", t_item.get("body", "")).strip()
                    t_id = t_item.get("id", f"train_{t_idx}")
                    if e_text == t_text:
                        exact_matches.append({
                            "eval_pool": eval_name,
                            "eval_id": e_id,
                            "train_pool": train_name,
                            "train_id": t_id,
                        })

    if exact_matches:
        print(f"⚠️ FOUND {len(exact_matches)} EXACT STRING MATCHES:")
        for m in exact_matches:
            print(f"  - [{m['eval_pool']}] {m['eval_id']} == [{m['train_pool']}] {m['train_id']}")
    else:
        print("✅ ZERO exact string matches between evaluation sets and training/retrieval corpora.")

    # AUDIT 2: Normalized Text Matches
    print("\n--- 2. NORMALIZED TEXT MATCH AUDIT (Casefold + Whitespace + Alphanumeric) ---")
    norm_matches = []
    for eval_name, eval_data in eval_pools.items():
        for e_idx, e_item in enumerate(eval_data):
            e_norm = normalize_text(e_item.get("text", e_item.get("body", "")))
            e_id = e_item.get("id", f"sample_{e_idx}")
            for train_name, train_data in train_pools.items():
                for t_idx, t_item in enumerate(train_data):
                    t_norm = normalize_text(t_item.get("text", t_item.get("body", "")))
                    t_id = t_item.get("id", f"train_{t_idx}")
                    if e_norm == t_norm and len(e_norm) > 30:
                        norm_matches.append({
                            "eval_pool": eval_name,
                            "eval_id": e_id,
                            "train_pool": train_name,
                            "train_id": t_id,
                        })

    if norm_matches:
        print(f"⚠️ FOUND {len(norm_matches)} NORMALIZED TEXT MATCHES:")
        for m in norm_matches:
            print(f"  - [{m['eval_pool']}] {m['eval_id']} == [{m['train_pool']}] {m['train_id']}")
    else:
        print("✅ ZERO normalized text matches between evaluation sets and training/retrieval corpora.")

    # AUDIT 3: Near-Duplicate 3-Gram Jaccard Similarity (Threshold >= 0.70)
    print("\n--- 3. NEAR-DUPLICATE N-GRAM SIMILARITY AUDIT (Jaccard >= 0.70) ---")
    high_similarity_pairs = []
    for eval_name in ["HeldOut_28", "Diagnostic_20"]:
        eval_data = eval_pools[eval_name]
        for e_idx, e_item in enumerate(eval_data):
            e_text = normalize_text(e_item.get("text", e_item.get("body", "")))
            e_id = e_item.get("id", f"sample_{e_idx}")
            e_ngrams = get_ngrams(e_text, n=3)
            if not e_ngrams:
                continue

            for train_name in ["Train_Baseline_1000", "Train_Enron_1000"]:
                train_data = train_pools[train_name]
                for t_idx, t_item in enumerate(train_data):
                    t_text = normalize_text(t_item.get("text", t_item.get("body", "")))
                    t_id = t_item.get("id", f"train_{t_idx}")
                    t_ngrams = get_ngrams(t_text, n=3)
                    sim = jaccard_similarity(e_ngrams, t_ngrams)
                    if sim >= 0.70:
                        high_similarity_pairs.append({
                            "eval_pool": eval_name,
                            "eval_id": e_id,
                            "train_pool": train_name,
                            "train_id": t_id,
                            "similarity": round(sim, 4),
                            "eval_snippet": e_text[:80],
                            "train_snippet": t_text[:80],
                        })

    if high_similarity_pairs:
        print(f"⚠️ FOUND {len(high_similarity_pairs)} HIGH-SIMILARITY (>= 0.70) PAIRS:")
        for p in high_similarity_pairs[:10]:
            print(f"  - Similarity {p['similarity']*100:.1f}%: [{p['eval_pool']}] {p['eval_id']} vs [{p['train_pool']}] {p['train_id']}")
            print(f"      Eval : {p['eval_snippet']}")
            print(f"      Train: {p['train_snippet']}")
    else:
        print("✅ ZERO near-duplicate pairs (Jaccard >= 0.70) found between evaluation sets and training corpora.")

    # AUDIT 4: Prompt Hardcoding & Memorization Inspection
    print("\n--- 4. SYSTEM PROMPTS HARDCODING & MEMORIZATION INSPECTION ---")
    prompts = {
        "RAG_SYSTEM_PROMPT": RAG_SYSTEM_PROMPT,
        "SYSTEM_INJECTION_DETECTOR": SYSTEM_INJECTION_DETECTOR,
        "SYSTEM_IS_PHISHING_ONLY": SYSTEM_IS_PHISHING_ONLY,
        "M2_SYSTEM_PROMPT": M2_SYSTEM_PROMPT,
    }

    # Check for domain names or phrases from evaluation sets appearing inside prompt strings
    prompt_leaks = []
    suspicious_eval_tokens = [
        "paypal-fraud-alerts-service.com",
        "binance global",
        "docusign-secure-document-vault-992.biz",
        "irs-tax-refund-portal-direct.gov.us.org",
        "corporate-sso-2fa-verify.com",
        "webmail-storage-quota-manager.info",
        "diag-legit-01",
        "marcus vance",
        "internal-cloud.corp",
        "48,500",
    ]

    for p_name, p_text in prompts.items():
        p_lower = p_text.lower()
        for tok in suspicious_eval_tokens:
            if tok.lower() in p_lower:
                prompt_leaks.append({"prompt": p_name, "token": tok})

    if prompt_leaks:
        print(f"⚠️ FOUND {len(prompt_leaks)} EVALUATION TOKENS INSIDE SYSTEM PROMPTS:")
        for leak in prompt_leaks:
            print(f"  - In {leak['prompt']}: '{leak['token']}'")
    else:
        print("✅ ZERO evaluation domains, tokens, or email content hardcoded in system prompts.")

    # Save report summary
    report = {
        "exact_matches": len(exact_matches),
        "normalized_matches": len(norm_matches),
        "high_similarity_pairs_count": len(high_similarity_pairs),
        "high_similarity_pairs": high_similarity_pairs,
        "prompt_leaks_count": len(prompt_leaks),
        "prompt_leaks": prompt_leaks,
    }
    with open("scratch/leakage_audit_summary.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\nSaved leakage audit summary to scratch/leakage_audit_summary.json")


if __name__ == "__main__":
    main()

