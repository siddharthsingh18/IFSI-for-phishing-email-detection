"""Audit whether dataset source or formatting shortcuts predict the label."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from email import policy
from email.parser import Parser
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeClassifier

from phishbench.data_loader import normalize_key


def _records(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train = [json.loads(line) for line in (root / "train.jsonl").read_text().splitlines() if line.strip()]
    test_path = root / "test.jsonl"
    test = [json.loads(line) for line in test_path.read_text().splitlines() if line.strip()] if test_path.exists() else []
    return train, test


def _mi(rows: list[dict[str, Any]]) -> tuple[float, float]:
    n = len(rows)
    joint = Counter((str(row.get("source")), _label(row)) for row in rows)
    source = Counter(str(row.get("source")) for row in rows)
    labels = Counter(_label(row) for row in rows)
    value = 0.0
    for (s, label), count in joint.items():
        value += count / n * math.log((count * n) / (source[s] * labels[label]))
    h_source = -sum((count / n) * math.log(count / n) for count in source.values())
    h_label = -sum((count / n) * math.log(count / n) for count in labels.values())
    return value, value / math.sqrt(h_source * h_label) if h_source and h_label else 0.0


def _split_eval(train: list[dict[str, Any]], test: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if test:
        return train, test
    ordered = list(train)
    midpoint = max(1, int(len(ordered) * 0.8))
    return ordered[:midpoint], ordered[midpoint:]


def _label(row: dict[str, Any]) -> int:
    return 1 if row["label"] in (1, "1", "phishing", "spam", "true") else 0


def _score(model: Any, x_train: Any, y_train: list[int], x_test: Any, y_test: list[int]) -> dict[str, float]:
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    return {
        "accuracy": float(accuracy_score(y_test, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
    }


def _format_features(text: str) -> dict[str, float]:
    message = Parser(policy=policy.default).parsestr(text)
    headers = {key.lower() for key in message.keys()}
    body = message.get_body(preferencelist=("plain", "html"))
    raw_body = body.get_content() if body else message.get_payload(decode=True) or ""
    if not isinstance(raw_body, str):
        raw_body = raw_body.decode("utf-8", errors="replace")
    urls = len(re.findall(r"https?://|www\.", text, flags=re.I))
    return {
        **{f"header:{key}": 1.0 for key in sorted(headers)},
        "mime:multipart": float(message.is_multipart()),
        "mime:html": float("html" in (message.get_content_type() or "").lower() or "<html" in raw_body.lower()),
        "mime:parts": float(sum(1 for _ in message.walk())),
        "style:crlf": float("\r\n" in text),
        "style:lf": float("\n" in text and "\r\n" not in text),
        "length:short": float(len(text) < 500),
        "length:medium": float(500 <= len(text) < 2000),
        "length:long": float(len(text) >= 2000),
        "non_ascii_ratio": sum(ord(char) > 127 for char in text) / max(1, len(text)),
        "url_count": float(urls),
    }


def _normalized(text: str) -> str:
    message = Parser(policy=policy.default).parsestr(text)
    subject = message.get("Subject", "")
    sender = message.get("From", "")
    domain = sender.rsplit("@", 1)[-1].strip(" >") if "@" in sender else ""
    body = message.get_body(preferencelist=("plain", "html"))
    body_text = body.get_content() if body else message.get_payload(decode=True) or ""
    if not isinstance(body_text, str):
        body_text = body_text.decode("utf-8", errors="replace")
    return normalize_key(f"From-domain: {domain}\nSubject: {subject}\nBody: {body_text}")


def _format_matrix(rows: list[dict[str, Any]], names: list[str] | None = None) -> tuple[list[list[float]], list[str]]:
    features = [_format_features(str(row["text"])) for row in rows]
    names = names or sorted({name for item in features for name in item})
    return [[item.get(name, 0.0) for name in names] for item in features], names


def _run_audit(train: list[dict[str, Any]], test: list[dict[str, Any]]) -> dict[str, Any]:
    train, test = _split_eval(train, test)
    y_train = [_label(row) for row in train]
    y_test = [_label(row) for row in test]
    source = ColumnTransformer([("source", OneHotEncoder(handle_unknown="ignore"), [0])])
    x_source_train = [[str(row.get("source"))] for row in train]
    x_source_test = [[str(row.get("source"))] for row in test]
    source_models = {
        "majority": [[0] for _ in train],
        "logistic_regression": make_pipeline(source, LogisticRegression(max_iter=500)),
        "decision_tree": make_pipeline(source, DecisionTreeClassifier(max_depth=4, random_state=42)),
    }
    source_scores: dict[str, Any] = {}
    majority = Counter(y_train).most_common(1)[0][0]
    source_scores["majority"] = {
        "accuracy": float(accuracy_score(y_test, [majority] * len(y_test))),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, [majority] * len(y_test))),
    }
    for name in ("logistic_regression", "decision_tree"):
        source_scores[name] = _score(source_models[name], x_source_train, y_train, x_source_test, y_test)

    format_train, names = _format_matrix(train)
    format_test, _ = _format_matrix(test, names)
    format_model = LogisticRegression(max_iter=500)
    format_scores = _score(format_model, format_train, y_train, format_test, y_test)
    coefficients = getattr(format_model, "coef_", [[0.0]])[0]
    format_scores["top_features"] = [
        name for _, name in sorted(zip(map(abs, coefficients), names), reverse=True)[:10]
    ]

    def text_scores(
        texts_train: list[str], labels_train: list[int],
        texts_test: list[str], labels_test: list[int],
    ) -> dict[str, float]:
        return _score(
            make_pipeline(TfidfVectorizer(min_df=1), LogisticRegression(max_iter=500)),
            texts_train, labels_train, texts_test, labels_test,
        )

    full_text = text_scores(
        [str(row["text"]) for row in train], y_train,
        [str(row["text"]) for row in test], y_test,
    )
    body_text = text_scores(
        [_normalized(str(row["text"])) for row in train], y_train,
        [_normalized(str(row["text"])) for row in test], y_test,
    )
    within_source: dict[str, Any] = {}
    for source_name in sorted({str(row.get("source")) for row in train + test}):
        subset = [row for row in train + test if str(row.get("source")) == source_name]
        if len({_label(row) for row in subset}) < 2:
            continue
        fit = [row for row in train if str(row.get("source")) == source_name]
        evaluate = [row for row in test if str(row.get("source")) == source_name]
        if len({_label(row) for row in fit}) < 2 or not evaluate:
            continue
        within_source[source_name] = text_scores(
            [str(row["text"]) for row in fit], [_label(row) for row in fit],
            [str(row["text"]) for row in evaluate], [_label(row) for row in evaluate],
        )
    source_table = {
        source_name: {
            "legit": sum(_label(row) == 0 for row in train + test if str(row.get("source")) == source_name),
            "phishing": sum(_label(row) == 1 for row in train + test if str(row.get("source")) == source_name),
        }
        for source_name in sorted({str(row.get("source")) for row in train + test})
    }
    mi, nmi = _mi(train + test)
    return {
        "source_x_label": source_table,
        "mutual_information": mi,
        "normalized_mutual_information": nmi,
        "source_only": source_scores,
        "format_only": format_scores,
        "full_text": full_text,
        "body_only_normalized": body_text,
        "within_source_full_text": within_source,
        "evaluation_counts": {"train": len(train), "test": len(test)},
    }


def audit_corpus(root: Path, config_path: Path | None = None, normalize: bool = False) -> dict[str, Any]:
    train, test = _records(root)
    raw = _run_audit(train, test)
    normalized = None
    if normalize:
        normalized = _run_audit(
            [{**row, "text": _normalized(str(row["text"]))} for row in train],
            [{**row, "text": _normalized(str(row["text"]))} for row in test],
        )
    config = json.loads(config_path.read_text()) if config_path else {}
    thresholds = config.get("roles", {}).get("primary", {}).get("confounding", {
        "source_only_balanced_accuracy_max": 0.65,
        "format_only_balanced_accuracy_max": 0.85,
        "full_minus_format_balanced_accuracy_min": 0.05,
    })
    source_ba = max(item["balanced_accuracy"] for item in raw["source_only"].values())
    format_ba = raw["format_only"]["balanced_accuracy"]
    full_ba = raw["full_text"]["balanced_accuracy"]
    reasons = []
    if source_ba > thresholds["source_only_balanced_accuracy_max"]:
        reasons.append("source-only balanced accuracy exceeds the configured threshold")
    if format_ba > thresholds["format_only_balanced_accuracy_max"]:
        reasons.append("format-only balanced accuracy exceeds the configured threshold")
    if full_ba - format_ba < thresholds["full_minus_format_balanced_accuracy_min"]:
        reasons.append("full-text balanced accuracy does not beat format-only performance by the configured margin")
    result = {
        "corpus": str(root),
        "raw": raw,
        "normalized": normalized,
        "thresholds": thresholds,
        "gate": {"passed": not reasons, "suitable_for_primary": not reasons, "reasons": reasons},
        "note": "Residual source-label correlation cannot be eliminated by gating alone; source-held-out results must accompany any headline number.",
    }
    (root / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    status = "is" if not reasons else "is not"
    reason_text = "; ".join(reasons) if reasons else "all configured thresholds passed"
    source_rows = "\n".join(
        f"| {name} | {values['legit']} | {values['phishing']} | "
        f"{values['phishing'] / max(1, values['legit'] + values['phishing']):.4f} |"
        for name, values in raw["source_x_label"].items()
    )
    normalized_text = (
        f"\n\n## Normalized preprocessing\n\n"
        f"- Source-only balanced accuracy: {max(item['balanced_accuracy'] for item in normalized['source_only'].values()):.4f}\n"
        f"- Format-only balanced accuracy: {normalized['format_only']['balanced_accuracy']:.4f}\n"
        f"- Full-text balanced accuracy: {normalized['full_text']['balanced_accuracy']:.4f}\n"
        if normalized else "\n\nNormalized preprocessing was not requested.\n"
    )
    (root / "audit.md").write_text(
        f"# Confounding audit\n\nThis corpus **{status} suitable for primary benchmarking**: {reason_text}.\n\n"
        f"{result['note']}\n\n"
        "## Source x label\n\n| Source | Legit | Phishing | Phishing rate |\n|---|---:|---:|---:|\n"
        f"{source_rows}\n\n"
        f"Mutual information: {raw['mutual_information']:.4f}\n\n"
        f"Normalized mutual information: {raw['normalized_mutual_information']:.4f}\n\n"
        f"Source-only balanced accuracy (maximum classifier): {source_ba:.4f}\n\n"
        f"Format-only balanced accuracy: {format_ba:.4f}\n\n"
        f"Full-text balanced accuracy: {full_ba:.4f}\n"
        f"{normalized_text}",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--config", type=Path, default=Path("config/dataset_gates.yaml"))
    parser.add_argument("--normalize", action="store_true")
    args = parser.parse_args()
    result = audit_corpus(args.corpus, args.config, args.normalize)
    print(json.dumps(result["gate"], indent=2))


if __name__ == "__main__":
    main()
