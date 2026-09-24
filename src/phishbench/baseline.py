"""TF-IDF + LogisticRegression baseline for phishing email classification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def compute_metrics(y_true: Sequence[int], y_pred: Sequence[int]) -> dict[str, Any]:
    """Compute classification metrics: confusion matrix, precision, recall, F1, and FPR.

    Positive class = 1 (Phishing)
    Negative class = 0 (Legitimate)

    Confusion Matrix Layout:
        [[TN, FP],
         [FN, TP]]

    Definitions:
        Precision = TP / (TP + FP)
        Recall    = TP / (TP + FN)
        F1        = 2 * Precision * Recall / (Precision + Recall)
        FPR       = FP / (FP + TN)
        Accuracy  = (TP + TN) / (TP + TN + FP + FN)
    """
    if len(y_true) != len(y_pred):
        raise ValueError(f"Length mismatch: len(y_true)={len(y_true)} vs len(y_pred)={len(y_pred)}")

    tn = fp = fn = tp = 0
    for yt, yp in zip(y_true, y_pred):
        yt_int = int(yt)
        yp_int = int(yp)
        if yt_int == 1 and yp_int == 1:
            tp += 1
        elif yt_int == 1 and yp_int == 0:
            fn += 1
        elif yt_int == 0 and yp_int == 1:
            fp += 1
        elif yt_int == 0 and yp_int == 0:
            tn += 1
        else:
            raise ValueError(f"Labels must be 0 or 1, found y_true={yt}, y_pred={yp}")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0.0

    return {
        "confusion_matrix": [
            [tn, fp],
            [fn, tp],
        ],
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "true_positives": tp,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "accuracy": accuracy,
        "total_samples": total,
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file."""
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def train_and_evaluate_baseline(
    train_path: Path,
    test_path: Path,
    output_path: Path | None = None,
    max_features: int = 10000,
    seed: int = 42,
) -> dict[str, Any]:
    """Train TF-IDF + LogisticRegression baseline on train split and evaluate on test split."""
    train_records = load_jsonl(train_path)
    test_records = load_jsonl(test_path)

    X_train = [r["text"] for r in train_records]
    y_train = [int(r["label"]) for r in train_records]

    X_test = [r["text"] for r in test_records]
    y_test = [int(r["label"]) for r in test_records]

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words="english",
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    classifier = LogisticRegression(
        random_state=seed,
        max_iter=1000,
        C=1.0,
    )
    classifier.fit(X_train_vec, y_train)

    y_pred = classifier.predict(X_test_vec)
    metrics = compute_metrics(y_test, y_pred)

    result = {
        "model": "TF-IDF + LogisticRegression",
        "hyperparameters": {
            "max_features": max_features,
            "stop_words": "english",
            "sublinear_tf": True,
            "classifier": "LogisticRegression",
            "C": 1.0,
            "seed": seed,
        },
        "train_samples": len(train_records),
        "test_samples": len(test_records),
        "metrics": metrics,
    }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=Path("data/splits/train.jsonl"), help="Path to train split")
    parser.add_argument("--test", type=Path, default=Path("data/splits/test.jsonl"), help="Path to test split")
    parser.add_argument("--output", type=Path, default=Path("results/baseline.json"), help="Output results path")
    parser.add_argument("--max-features", type=int, default=10000, help="Max vocabulary features")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    results = train_and_evaluate_baseline(
        train_path=args.train,
        test_path=args.test,
        output_path=args.output,
        max_features=args.max_features,
        seed=args.seed,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
