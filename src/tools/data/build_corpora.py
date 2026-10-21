"""Build explicitly roled corpora from a cleaned provenance-preserving JSONL pool."""

from __future__ import annotations

import argparse
import hashlib
import os
import json
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from phishbench.data_loader import (
    cluster_near_duplicates,
    normalize_key,
    split_by_regime,
    validate_split_records,
)


def _load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_pool(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def _cluster_sample(records: list[dict[str, Any]], target: int, seed: int) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[str(record.get("cluster_id") or record["id"])].append(record)
    rng = random.Random(seed)
    candidates = list(groups.values())
    rng.shuffle(candidates)
    selected: list[dict[str, Any]] = []
    for group in candidates:
        if len(selected) + len(group) <= target or not selected:
            selected.extend(group)
    return selected


def _cap_source(records: list[dict[str, Any]], max_share: float, seed: int) -> list[dict[str, Any]]:
    target = max(1, int(len(records) / max_share)) if max_share < 1 else len(records)
    return _cluster_sample(records, target, seed) if len(records) > target else records


def _cap_epvme(records: list[dict[str, Any]], definition: dict[str, Any], seed: int) -> list[dict[str, Any]]:
    result = records
    for field, cap_key in (("family", "max_family_share"), ("header_scaffold_fingerprint", "max_header_scaffold_share")):
        cap = definition.get(cap_key)
        if not cap:
            continue
        groups = defaultdict(list)
        for row in result:
            groups[str(row.get(field, "unknown"))].append(row)
        total = len(result)
        per_group_target = max(1, int(total * cap))
        result = [
            item
            for group in groups.values()
            for item in _cluster_sample(group, per_group_target, seed)
        ]
    return result


def _report(records: list[dict[str, Any]], gate: dict[str, Any], regime: str | None = None) -> dict[str, Any]:
    source_label = Counter((str(row.get("source")), str(row.get("label"))) for row in records)
    source_counts = Counter(str(row.get("source")) for row in records)
    family_counts = Counter(str(row.get("family", "unknown")) for row in records)
    total = len(records)
    return {
        "total": total,
        "counts_by_source_label": {
            f"{source}:{label}": count for (source, label), count in sorted(source_label.items())
        },
        "source_shares": {source: count / total if total else 0 for source, count in sorted(source_counts.items())},
        "class_balance": {
            "phishing": sum(row.get("label") in (1, "1", "phishing") for row in records),
            "legit": sum(row.get("label") in (0, "0", "legit", "legitimate") for row in records),
        },
        "family_counts": dict(sorted(family_counts.items())),
        "gates": gate,
        **({"regime": regime} if regime else {}),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_regime(
    records: list[dict[str, Any]],
    output_dir: Path,
    *,
    regime: str,
    seed: int,
    held_out_source: str | None = None,
    held_out_family: str | None = None,
    held_out_template: str | None = None,
    recall_only: bool = False,
) -> dict[str, Any]:
    split = split_by_regime(
        records,
        regime=regime,
        seed=seed,
        held_out_source=held_out_source,
        held_out_family=held_out_family,
        held_out_template=held_out_template,
        recall_only=recall_only,
    )
    validation = validate_split_records(split)
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, rows in split.items():
        path = output_dir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        files[name] = {"path": str(path), "sha256": _sha256(path), "records": len(rows)}
    manifest = {
        "status": "complete",
        "git_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
        ).stdout.strip() or "unknown",
        "python": sys.version,
        "regime": regime,
        "seed": seed,
        "held_out_source": held_out_source,
        "held_out_family": held_out_family,
        "held_out_template": held_out_template,
        "validation": validation,
        "files": files,
    }
    (output_dir / "split_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def _build_corpora_impl(
    pool: Path,
    config: Path,
    output_root: Path,
    seed: int,
    regime: str = "random_stratified_grouped",
    held_out_source: str | None = None,
    held_out_family: str | None = None,
    held_out_template: str | None = None,
    recall_only: bool = False,
) -> dict[str, Any]:
    cfg = _load_config(config)
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite existing corpus directory: {output_root}")
    work_root = output_root.parent / "work"
    work_root.mkdir(parents=True, exist_ok=True)
    work_dir = work_root / f"{output_root.name}_{int(time.time())}_{seed}"
    work_dir.mkdir()
    records, cluster_stats = cluster_near_duplicates(_read_pool(pool))
    for record in records:
        record.setdefault("family", "unknown")
    by_source = defaultdict(list)
    for record in records:
        by_source[str(record.get("source"))].append(record)

    outputs: dict[str, Any] = {}
    primary_cfg = cfg["corpora"]["primary_balanced"]
    missing_legit = [
        source for source, definition in cfg["sources"].items()
        if definition.get("role") == "legit" and not by_source.get(source)
    ]
    if missing_legit:
        (work_dir / "FAILED.json").write_text(
            json.dumps({
                "status": "failed",
                "reason": "primary_balanced cannot be built; missing legitimate sources: "
                + ", ".join(missing_legit),
            }, indent=2) + "\n",
            encoding="utf-8",
        )
        raise ValueError(
            "primary_balanced cannot be built; missing legitimate sources: "
            + ", ".join(missing_legit)
        )

    selected: dict[str, list[dict[str, Any]]] = {}
    for name, corpus_cfg in cfg["corpora"].items():
        if name == "injection_resilience":
            continue
        if corpus_cfg.get("include_sources"):
            rows = [record for source in corpus_cfg["include_sources"] for record in by_source.get(source, [])]
        else:
            rows = [
                record for record in records
                if cfg["sources"].get(str(record.get("source")), {}).get("role") in corpus_cfg.get("include_roles", [])
                and str(record.get("source")) not in corpus_cfg.get("exclude_sources", [])
            ]
        max_share = corpus_cfg.get("max_source_share")
        if max_share:
            capped = []
            for source in sorted({str(row.get("source")) for row in rows}):
                capped.extend(_cap_source([row for row in rows if str(row.get("source")) == source], max_share, seed))
            rows = capped
        if "epvme" in corpus_cfg.get("include_sources", []):
            rows = _cap_epvme(rows, cfg["sources"]["epvme"], seed)
        if name == "primary_balanced":
            low, high = corpus_cfg["target_phishing_share"]
            phishing = [row for row in rows if row.get("label") in ("phishing", 1, "1")]
            legit = [row for row in rows if row.get("label") in ("legit", "legitimate", 0, "0")]
            target_phishing = int(len(legit) * high / (1 - high))
            rows = legit + _cluster_sample(phishing, target_phishing, seed)
            share = len([row for row in rows if row in phishing]) / len(rows)
            if not low <= share <= high:
                raise ValueError(f"primary_balanced target phishing share failed: {share:.3f}")
        selected[name] = rows

    injection_by_id = {
        str(record["id"]): record
        for record in selected["primary_balanced"] + selected["legit_controls"]
    }
    selected["injection_resilience"] = list(injection_by_id.values())
    for name, rows in selected.items():
        corpus_dir = work_dir / name
        corpus_dir.mkdir(parents=True, exist_ok=True)
        split_manifest = write_regime(
            rows,
            corpus_dir,
            regime=regime,
            seed=seed,
            held_out_source=held_out_source,
            held_out_family=held_out_family,
            held_out_template=held_out_template,
            recall_only=recall_only,
        )
        gate = {
            "passed": split_manifest["validation"]["is_valid"],
            "metrics_policy": cfg["corpora"].get(name, {}).get("metrics_policy", "full"),
        }
        report = _report(rows, gate, regime)
        report["cluster_stats"] = cluster_stats
        (corpus_dir / "corpus_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        outputs[name] = report
    output_root.parent.mkdir(parents=True, exist_ok=True)
    os.replace(work_dir, output_root)
    return outputs


def build_corpora(
    pool: Path,
    config: Path,
    output_root: Path,
    seed: int,
    regime: str = "random_stratified_grouped",
    held_out_source: str | None = None,
    held_out_family: str | None = None,
    held_out_template: str | None = None,
    recall_only: bool = False,
) -> dict[str, Any]:
    try:
        return _build_corpora_impl(
            pool, config, output_root, seed, regime, held_out_source,
            held_out_family, held_out_template, recall_only,
        )
    except Exception as exc:
        work_root = output_root.parent / "work"
        candidates = sorted(
            work_root.glob(f"{output_root.name}_*"),
            key=lambda path: path.stat().st_mtime,
        ) if work_root.exists() else []
        if candidates:
            (candidates[-1] / "FAILED.json").write_text(
                json.dumps({"status": "failed", "reason": str(exc)}, indent=2) + "\n",
                encoding="utf-8",
            )
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("config/corpora.yaml"))
    parser.add_argument("--output-root", type=Path, default=Path("data/corpora"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--regime", choices=("random_stratified_grouped", "source_held_out", "family_held_out", "template_held_out"), default="random_stratified_grouped")
    parser.add_argument("--held-out-source")
    parser.add_argument("--held-out-family")
    parser.add_argument("--held-out-template")
    parser.add_argument("--recall-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build_corpora(
        args.pool, args.config, args.output_root, args.seed,
        args.regime, args.held_out_source, args.held_out_family,
        args.held_out_template, args.recall_only,
    ), indent=2))


if __name__ == "__main__":
    main()
