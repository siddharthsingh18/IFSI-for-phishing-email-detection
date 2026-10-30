"""Phase 2: Systematic Retraining, Threshold Tuning, and Generalization Audit for M1.

Evaluates M1 TF-IDF + LogisticRegression on:
1. Validation set tuning (regularization C, class weights, n-gram range, decision threshold)
2. Final test set (N=173) under default (0.50) and validation-tuned threshold (0.13)
3. Diagnostic suite (N=20) under default (0.50) and validation-tuned threshold (0.13)
4. Vocabulary feature attribution and overfitting analysis
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT_DIR = Path(__file__).resolve().parents[1]
src_dir = ROOT_DIR / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from phishbench.baseline import compute_metrics, load_jsonl


def load_diagnostic_suite(path: Path) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = []
    cases = data if isinstance(data, list) else data.get("cases", [])
    for item in cases:
        items.append({
            "id": item.get("id"),
            "text": item.get("text", item.get("body", item.get("injected_text", ""))),
            "label": int(item.get("true_label", 1 if item.get("ground_truth") == "phishing" else 0)),
            "category": item.get("category", "unknown"),
        })
    return items


def evaluate_threshold(y_true: list[int], probs: np.ndarray, tau: float) -> dict[str, Any]:
    preds = (probs >= tau).astype(int)
    m = compute_metrics(y_true, preds)
    fnr = m["false_negatives"] / (m["false_negatives"] + m["true_positives"]) if (m["false_negatives"] + m["true_positives"]) > 0 else 0.0
    m["fnr"] = fnr
    m["threshold"] = tau
    return m


def main():
    print("=" * 80)
    print("PHASE 2: M1 RETRAINING AND HYPERPARAMETER SELECTION")
    print("=" * 80)

    clean_dir = ROOT_DIR / "data" / "splits" / "clean_split_v1"
    train_records = load_jsonl(clean_dir / "train.jsonl")
    val_records = load_jsonl(clean_dir / "val.jsonl")
    test_records = load_jsonl(clean_dir / "test.jsonl")
    diag_records = load_diagnostic_suite(ROOT_DIR / "data" / "diagnostic_suite.json")

    X_train = [r["text"] for r in train_records]
    y_train = [int(r["label"]) for r in train_records]

    X_val = [r["text"] for r in val_records]
    y_val = [int(r["label"]) for r in val_records]

    X_test = [r["text"] for r in test_records]
    y_test = [int(r["label"]) for r in test_records]

    X_diag = [r["text"] for r in diag_records]
    y_diag = [int(r["label"]) for r in diag_records]

    # Grid search on validation split for C and class_weight
    param_grid = [
        {"ngram_range": (1, 1), "C": 0.1, "class_weight": None, "sublinear_tf": True},
        {"ngram_range": (1, 1), "C": 1.0, "class_weight": None, "sublinear_tf": True},
        {"ngram_range": (1, 1), "C": 1.0, "class_weight": "balanced", "sublinear_tf": True},
        {"ngram_range": (1, 1), "C": 5.0, "class_weight": None, "sublinear_tf": True},
        {"ngram_range": (1, 2), "C": 1.0, "class_weight": "balanced", "sublinear_tf": True},
    ]

    best_roc_auc = -1.0
    best_config = None
    best_vec = None
    best_clf = None

    for params in param_grid:
        vec = TfidfVectorizer(
            ngram_range=params["ngram_range"],
            max_features=10000,
            stop_words="english",
            sublinear_tf=params["sublinear_tf"],
        )
        X_tr = vec.fit_transform(X_train)
        X_v = vec.transform(X_val)

        clf = LogisticRegression(
            C=params["C"],
            class_weight=params["class_weight"],
            random_state=42,
            max_iter=1000,
        )
        clf.fit(X_tr, y_train)

        probs_v = clf.predict_proba(X_v)[:, 1]
        auc = roc_auc_score(y_val, probs_v)
        ap = average_precision_score(y_val, probs_v)

        if auc > best_roc_auc:
            best_roc_auc = auc
            best_config = params
            best_vec = vec
            best_clf = clf

    # Fit final model with best hyperparameters strictly on training set
    X_train_vec = best_vec.transform(X_train)
    X_val_vec = best_vec.transform(X_val)
    X_test_vec = best_vec.transform(X_test)
    X_diag_vec = best_vec.transform(X_diag)

    val_probs = best_clf.predict_proba(X_val_vec)[:, 1]
    test_probs = best_clf.predict_proba(X_test_vec)[:, 1]
    diag_probs = best_clf.predict_proba(X_diag_vec)[:, 1]

    # Tune threshold on validation set
    thresholds = [i / 100.0 for i in range(5, 95, 2)]
    best_val_tau = 0.50
    best_val_f1 = -1.0
    for tau in thresholds:
        m = evaluate_threshold(y_val, val_probs, tau)
        if m["f1"] > best_val_f1 or (abs(m["f1"] - best_val_f1) < 1e-4 and m["fpr"] < 0.05):
            best_val_f1 = m["f1"]
            best_val_tau = tau

    print(f"Validation Tuning Complete:")
    print(f"  Best Config:       {best_config}")
    print(f"  Val ROC-AUC:       {roc_auc_score(y_val, val_probs):.4f}")
    print(f"  Val PR-AUC:        {average_precision_score(y_val, val_probs):.4f}")
    print(f"  Optimal Threshold: {best_val_tau:.2f} (Val F1={best_val_f1:.4f})")

    # Evaluate at default threshold 0.50
    test_m_def = evaluate_threshold(y_test, test_probs, 0.50)
    diag_m_def = evaluate_threshold(y_diag, diag_probs, 0.50)

    # Evaluate at validation-tuned threshold best_val_tau
    test_m_tuned = evaluate_threshold(y_test, test_probs, best_val_tau)
    diag_m_tuned = evaluate_threshold(y_diag, diag_probs, best_val_tau)

    # Compare with old baseline model
    old_train_records = load_jsonl(ROOT_DIR / "data" / "splits" / "review_seed42" / "train.jsonl")
    old_vec = TfidfVectorizer(max_features=10000, stop_words="english", sublinear_tf=True)
    old_X_tr = old_vec.fit_transform([r["text"] for r in old_train_records])
    old_clf = LogisticRegression(C=1.0, random_state=42, max_iter=200, class_weight="balanced")
    old_clf.fit(old_X_tr, [int(r["label"]) for r in old_train_records])

    old_test_preds = old_clf.predict(old_vec.transform(X_test))
    old_diag_preds = old_clf.predict(old_vec.transform(X_diag))
    old_test_m = compute_metrics(y_test, old_test_preds)
    old_diag_m = compute_metrics(y_diag, old_diag_preds)

    print("\n" + "=" * 80)
    print("M1 PERFORMANCE COMPARISON (OLD VS RETRAINED)")
    print("=" * 80)
    print(f"{'Metric':<18} | {'Old Baseline':<14} | {'Retrained (tau=0.5)':<20} | {'Retrained (tau=0.13)':<20}")
    print("-" * 80)
    print(f"{'Accuracy':<18} | {old_test_m['accuracy']:.4f}         | {test_m_def['accuracy']:.4f}               | {test_m_tuned['accuracy']:.4f}")
    print(f"{'Precision':<18} | {old_test_m['precision']:.4f}         | {test_m_def['precision']:.4f}               | {test_m_tuned['precision']:.4f}")
    print(f"{'Recall':<18} | {old_test_m['recall']:.4f}         | {test_m_def['recall']:.4f}               | {test_m_tuned['recall']:.4f}")
    print(f"{'F1-Score':<18} | {old_test_m['f1']:.4f}         | {test_m_def['f1']:.4f}               | {test_m_tuned['f1']:.4f}")
    print(f"{'FPR':<18} | {old_test_m['fpr']:.4f}         | {test_m_def['fpr']:.4f}               | {test_m_tuned['fpr']:.4f}")
    print(f"{'Confusion Matrix':<18} | {str(old_test_m['confusion_matrix']):<14} | {str(test_m_def['confusion_matrix']):<20} | {str(test_m_tuned['confusion_matrix']):<20}")

    print("\nOn Diagnostic Suite (N=20):")
    print(f"{'Metric':<18} | {'Old Baseline':<14} | {'Retrained (tau=0.5)':<20} | {'Retrained (tau=0.13)':<20}")
    print("-" * 80)
    print(f"{'Accuracy':<18} | {old_diag_m['accuracy']:.4f}         | {diag_m_def['accuracy']:.4f}               | {diag_m_tuned['accuracy']:.4f}")
    print(f"{'Precision':<18} | {old_diag_m['precision']:.4f}         | {diag_m_def['precision']:.4f}               | {diag_m_tuned['precision']:.4f}")
    print(f"{'Recall':<18} | {old_diag_m['recall']:.4f}         | {diag_m_def['recall']:.4f}               | {diag_m_tuned['recall']:.4f}")
    print(f"{'F1-Score':<18} | {old_diag_m['f1']:.4f}         | {diag_m_def['f1']:.4f}               | {diag_m_tuned['f1']:.4f}")
    print(f"{'FPR':<18} | {old_diag_m['fpr']:.4f}         | {diag_m_def['fpr']:.4f}               | {diag_m_tuned['fpr']:.4f}")
    print(f"{'Confusion Matrix':<18} | {str(old_diag_m['confusion_matrix']):<14} | {str(diag_m_def['confusion_matrix']):<20} | {str(diag_m_tuned['confusion_matrix']):<20}")

    # Feature weights
    feature_names = np.array(best_vec.get_feature_names_out())
    coefs = best_clf.coef_[0]
    top_phish = [(str(feature_names[i]), float(coefs[i])) for i in np.argsort(coefs)[-15:][::-1]]
    top_legit = [(str(feature_names[i]), float(coefs[i])) for i in np.argsort(coefs)[:15]]

    result_payload = {
        "model_name": "M1_TFIDF_LogisticRegression_Clean",
        "best_hyperparameters": best_config,
        "validation_tuned_threshold": best_val_tau,
        "clean_test_metrics_default_tau": test_m_def,
        "clean_test_metrics_tuned_tau": test_m_tuned,
        "diagnostic_metrics_default_tau": diag_m_def,
        "diagnostic_metrics_tuned_tau": diag_m_tuned,
        "baseline_old_metrics_clean_test": old_test_m,
        "baseline_old_metrics_diagnostic": old_diag_m,
        "top_phishing_features": top_phish,
        "top_legitimate_features": top_legit,
    }

    out_file = ROOT_DIR / "results" / "m1_clean_retrained.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)

    print(f"\nPersisted final M1 retrained results to {out_file}")


if __name__ == "__main__":
    main()
