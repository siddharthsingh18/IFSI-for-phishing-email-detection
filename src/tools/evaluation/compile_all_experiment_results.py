#!/usr/bin/env python3
"""Normalize DeepSeek and local Qwen results into one comparison artifact."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from phishbench.io import sha256_file, write_json


ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("phishfuzzer_seed_42", "nazario_enron_quality_seed_42")
METHODS = ("direct", "robust", "ours")


def metrics(tp: int, tn: int, fp: int, fn: int) -> dict[str, Any]:
    n = tp + tn + fp + fn
    precision = None if tp + fp == 0 else tp / (tp + fp)
    recall = None if tp + fn == 0 else tp / (tp + fn)
    fpr = None if fp + tn == 0 else fp / (fp + tn)
    f1 = (
        None
        if precision is None or recall is None or precision + recall == 0
        else 2 * precision * recall / (precision + recall)
    )
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return {
        "n": n,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": None if n == 0 else (tp + tn) / n,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "mcc": None if denominator == 0 else (tp * tn - fp * fn) / denominator,
    }


def combine_metrics(*values: dict[str, Any]) -> dict[str, Any]:
    return metrics(
        sum(int(value["tp"]) for value in values),
        sum(int(value["tn"]) for value in values),
        sum(int(value["fp"]) for value in values),
        sum(int(value["fn"]) for value in values),
    )


def exact_binomial_p(a_correct_b_wrong: int, a_wrong_b_correct: int) -> float:
    n = a_correct_b_wrong + a_wrong_b_correct
    if n == 0:
        return 1.0
    tail = sum(
        math.comb(n, k) for k in range(min(a_correct_b_wrong, a_wrong_b_correct) + 1)
    ) / (2**n)
    return min(1.0, 2 * tail)


def cell_counts(cell: dict[str, Any], deepseek: bool) -> dict[str, Any]:
    return cell["failure_as_error_metrics"] if deepseek else cell


def weighted_efficiency(cells: list[dict[str, Any]], deepseek: bool) -> dict[str, Any]:
    total_n = sum(
        int(cell["records_total"] if deepseek else cell["n"])
        for cell in cells
    )
    fields = ("answer_tokens", "reasoning_tokens")
    output: dict[str, Any] = {}
    for field in fields:
        total = 0.0
        records = 0
        for cell in cells:
            n = int(cell["records_total"] if deepseek else cell["n"])
            summary = cell["efficiency"][field] if deepseek else cell[field]
            if summary.get("mean") is not None:
                total += float(summary["mean"]) * n
                records += n
        output[field] = None if records == 0 else total / records
    if deepseek:
        totals = []
        weights = []
        for cell in cells:
            n = int(cell["records_total"])
            value = cell["efficiency"]["api_completion_tokens"].get("mean")
            if value is not None:
                totals.append(float(value) * n)
                weights.append(n)
        output["output_tokens_including_reasoning"] = (
            None if not weights else sum(totals) / sum(weights)
        )
        output["format_valid_rate"] = sum(
            float(cell["efficiency"]["format_valid_rate"]) * int(cell["records_total"])
            for cell in cells
        ) / total_n
    else:
        output["output_tokens_including_reasoning"] = sum(
            float(cell["output_tokens_including_reasoning"]["mean"]) * int(cell["n"])
            for cell in cells
        ) / total_n
        output["format_valid_rate"] = sum(
            float(cell["format_valid_rate"]) * int(cell["n"])
            for cell in cells
        ) / total_n
    output["records"] = total_n
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deepseek", type=Path, required=True)
    parser.add_argument("--qwen", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deepseek-raw-manifest", type=Path, required=True)
    parser.add_argument("--qwen-raw-manifest", type=Path, required=True)
    parser.add_argument("--portable-prompts", type=Path, required=True)
    args = parser.parse_args()

    def source_name(path: Path) -> str:
        resolved = path.resolve()
        try:
            return str(resolved.relative_to(ROOT))
        except ValueError:
            return str(resolved)

    deepseek = json.loads(args.deepseek.read_text(encoding="utf-8"))
    qwen = json.loads(args.qwen.read_text(encoding="utf-8"))
    configurations = [
        ("deepseek-v4-flash_non-thinking", "DeepSeek-v4-Flash", "non-thinking", "deepseek-v4-flash", "off"),
        ("deepseek-v4-flash_thinking", "DeepSeek-v4-Flash", "thinking", "deepseek-v4-flash", "on"),
        ("deepseek-v4-pro_non-thinking", "DeepSeek-v4-Pro", "non-thinking", "deepseek-v4-pro", "off"),
        ("deepseek-v4-pro_thinking", "DeepSeek-v4-Pro", "thinking", "deepseek-v4-pro", "on"),
        ("qwen3.5-9b_non-thinking", "Qwen3.5-9B", "non-thinking", None, None),
        ("qwen3.5-9b_thinking", "Qwen3.5-9B", "thinking", None, None),
        ("qwen3.5-35b-a3b_non-thinking", "Qwen3.5-35B-A3B", "non-thinking", None, None),
        ("qwen3.5-35b-a3b_thinking", "Qwen3.5-35B-A3B", "thinking", None, None),
    ]
    results: dict[str, Any] = {}
    for config_id, model, mode, ds_model, ds_thinking in configurations:
        is_deepseek = ds_model is not None
        source = deepseek if is_deepseek else qwen["runs"][config_id]
        config: dict[str, Any] = {"model": model, "mode": mode, "datasets": {}}
        efficiency_cells: dict[str, list[dict[str, Any]]] = {method: [] for method in METHODS}
        for dataset in DATASETS:
            dataset_result: dict[str, Any] = {"methods": {}}
            for method in METHODS:
                condition_cells: dict[str, dict[str, Any]] = {}
                for condition in ("clean", "attacked_phishing", "injected_legitimate_control"):
                    key = (
                        f"{dataset}|{ds_model}|{ds_thinking}|{method}|{condition}"
                        if is_deepseek
                        else f"{dataset}|{method}|{condition}"
                    )
                    cell = source["cells"][key]
                    condition_cells[condition] = cell
                    efficiency_cells[method].append(cell)
                clean = cell_counts(condition_cells["clean"], is_deepseek)
                attacked = cell_counts(condition_cells["attacked_phishing"], is_deepseek)
                control = cell_counts(
                    condition_cells["injected_legitimate_control"], is_deepseek
                )
                clean_metrics = metrics(clean["tp"], clean["tn"], clean["fp"], clean["fn"])
                injected_metrics = combine_metrics(attacked, control)
                dataset_result["methods"][method] = {
                    "no_prompt_injection": clean_metrics,
                    "prompt_injection": injected_metrics,
                    "attacked_phishing": metrics(
                        attacked["tp"], attacked["tn"], attacked["fp"], attacked["fn"]
                    ),
                    "injected_legitimate_control": metrics(
                        control["tp"], control["tn"], control["fp"], control["fn"]
                    ),
                    "prompt_injection_minus_no_injection": {
                        name: (
                            None
                            if clean_metrics[name] is None or injected_metrics[name] is None
                            else injected_metrics[name] - clean_metrics[name]
                        )
                        for name in ("accuracy", "precision", "recall", "f1", "fpr", "mcc")
                    },
                }

            ours = dataset_result["methods"]["ours"]
            robust = dataset_result["methods"]["robust"]
            direct = dataset_result["methods"]["direct"]
            if is_deepseek:
                comparison_prefix = f"{dataset}|{ds_model}|{ds_thinking}"
                mc = source["mcnemar_method_comparisons"]
                attacked_ro = mc[f"{comparison_prefix}|attacked_phishing|ours|robust"] if f"{comparison_prefix}|attacked_phishing|ours|robust" in mc else mc[f"{comparison_prefix}|attacked_phishing|robust|ours"]
                control_ro = mc[f"{comparison_prefix}|injected_legitimate_control|ours|robust"] if f"{comparison_prefix}|injected_legitimate_control|ours|robust" in mc else mc[f"{comparison_prefix}|injected_legitimate_control|robust|ours"]
                injection_key = f"{dataset}|{ds_model}|{ds_thinking}|ours"
                injection_metrics = source["paired_condition_changes"][injection_key]["injection_detection"]
            else:
                mc = source["mcnemar_method_comparisons"]
                attacked_ro = mc[f"{dataset}|attacked_phishing|robust|ours"]
                control_ro = mc[f"{dataset}|injected_legitimate_control|robust|ours"]
                injection_metrics = source["injection_detection"][f"{dataset}|ours"]
            a = int(attacked_ro["a_correct_b_wrong"])
            b = int(attacked_ro["a_wrong_b_correct"])
            c = int(control_ro["a_correct_b_wrong"])
            d = int(control_ro["a_wrong_b_correct"])
            dataset_result["ours_vs_robust"] = {
                "attacked_recall_delta_pp": 100
                * (ours["attacked_phishing"]["recall"] - robust["attacked_phishing"]["recall"]),
                "attacked_exact_mcnemar_p": attacked_ro["exact_two_sided_p"],
                "prompt_injection_accuracy_delta_pp": 100
                * (ours["prompt_injection"]["accuracy"] - robust["prompt_injection"]["accuracy"]),
                "prompt_injection_exact_mcnemar_p": exact_binomial_p(a + c, b + d),
            }
            best_clean_precision = max(
                direct["no_prompt_injection"]["precision"],
                robust["no_prompt_injection"]["precision"],
            )
            best_control_fpr = min(
                direct["injected_legitimate_control"]["fpr"],
                robust["injected_legitimate_control"]["fpr"],
            )
            dataset_result["hypothesis_checks"] = {
                "h1_ours_recall_above_both_baselines": ours["attacked_phishing"]["recall"]
                > max(
                    direct["attacked_phishing"]["recall"],
                    robust["attacked_phishing"]["recall"],
                ),
                "h2_clean_precision_within_2pp": ours["no_prompt_injection"]["precision"]
                >= best_clean_precision - 0.02,
                "h2_control_fpr_within_2pp": ours["injected_legitimate_control"]["fpr"]
                <= best_control_fpr + 0.02,
            }
            dataset_result["ours_injection_detection"] = injection_metrics
            config["datasets"][dataset] = dataset_result
        config["efficiency"] = {
            method: weighted_efficiency(efficiency_cells[method], is_deepseek)
            for method in METHODS
        }
        results[config_id] = config

    ablation: dict[str, Any] = {}
    for config_id, run in qwen["runs"].items():
        if "phishfuzzer_seed_42|ours_no_summary" not in run.get(
            "prompt_injection_environment_comparison", {}
        ):
            continue
        ablation[config_id] = {
            method: run["prompt_injection_environment_comparison"][
                f"phishfuzzer_seed_42|{method}"
            ]
            for method in ("ours", "ours_no_summary")
        }

    write_json(
        args.output,
        {
            "format": "phishbench-all-model-results-v1",
            "sources": {
                source_name(args.deepseek_raw_manifest): sha256_file(
                    args.deepseek_raw_manifest
                ),
                source_name(args.qwen_raw_manifest): sha256_file(
                    args.qwen_raw_manifest
                ),
                source_name(args.portable_prompts): sha256_file(
                    args.portable_prompts
                ),
            },
            "dataset_order": list(DATASETS),
            "configuration_order": [item[0] for item in configurations],
            "results": results,
            "qwen_ours_no_summary_ablation": ablation,
        },
    )
    print(json.dumps({"configurations": len(results), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
