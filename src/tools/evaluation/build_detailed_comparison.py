#!/usr/bin/env python3
"""Build the detailed condition-level comparison directly from retained artifacts."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from phishbench.runner import parse_output


CONFIGURATIONS = (
    "deepseek-v4-flash_non-thinking",
    "deepseek-v4-flash_thinking",
    "deepseek-v4-pro_non-thinking",
    "deepseek-v4-pro_thinking",
    "qwen3.5-9b_non-thinking",
    "qwen3.5-9b_thinking",
    "qwen3.5-35b-a3b_non-thinking",
    "qwen3.5-35b-a3b_thinking",
)
MODEL_GROUPS = (
    (
        "DeepSeek-v4-Flash",
        ("deepseek-v4-flash_non-thinking", "deepseek-v4-flash_thinking"),
    ),
    (
        "DeepSeek-v4-Pro",
        ("deepseek-v4-pro_non-thinking", "deepseek-v4-pro_thinking"),
    ),
    (
        "Qwen3.5-9B",
        ("qwen3.5-9b_non-thinking", "qwen3.5-9b_thinking"),
    ),
    (
        "Qwen3.5-35B-A3B",
        ("qwen3.5-35b-a3b_non-thinking", "qwen3.5-35b-a3b_thinking"),
    ),
)
DATASETS = ("phishfuzzer_seed_42", "nazario_enron_quality_seed_42")
METHODS = ("direct", "robust", "ours")
CONDITIONS = ("clean", "attacked_phishing", "injected_legitimate_control")

CONFIG_LABELS = {
    "deepseek-v4-flash_non-thinking": "DeepSeek-v4-Flash / non-thinking",
    "deepseek-v4-flash_thinking": "DeepSeek-v4-Flash / thinking",
    "deepseek-v4-pro_non-thinking": "DeepSeek-v4-Pro / non-thinking",
    "deepseek-v4-pro_thinking": "DeepSeek-v4-Pro / thinking",
    "qwen3.5-9b_non-thinking": "Qwen3.5-9B / non-thinking",
    "qwen3.5-9b_thinking": "Qwen3.5-9B / thinking",
    "qwen3.5-35b-a3b_non-thinking": "Qwen3.5-35B-A3B / non-thinking",
    "qwen3.5-35b-a3b_thinking": "Qwen3.5-35B-A3B / thinking",
}
DATASET_LABELS = {
    "phishfuzzer_seed_42": "PhishFuzzer",
    "nazario_enron_quality_seed_42": "质量修正的 Nazario + Enron",
}
CONDITION_LABELS = {
    "clean": "无注入",
    "attacked_phishing": "黑注入",
    "injected_legitimate_control": "白注入",
}


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def fmt_metric(value: float | None) -> str:
    return "—" if value is None else f"{value:.3f}"


def fmt_percent(value: float | None) -> str:
    return "—" if value is None else f"{100 * value:.2f}%"


def fmt_token(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f}"


def emphasized(text: str, value: float | None, best: float | None) -> str:
    if value is None or best is None:
        return text
    numeric_text = text.removesuffix("%")
    decimals = len(numeric_text.partition(".")[2])
    displayed_best = 100 * best if text.endswith("%") else best
    best_text = f"{displayed_best:.{decimals}f}" + ("%" if text.endswith("%") else "")
    return f"**{text}**" if text == best_text else text


def optimum(values: list[float | None], maximize: bool) -> float | None:
    available = [value for value in values if value is not None]
    if not available:
        return None
    return max(available) if maximize else min(available)


def deepseek_config(row: dict[str, Any]) -> str:
    mode = "thinking" if row["thinking"] == "on" else "non-thinking"
    return f"{row['model_requested']}_{mode}"


def collect_token_stats(
    deepseek_dir: Path, qwen_dir: Path
) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    cells: dict[tuple[str, str, str, str], dict[str, Any]] = defaultdict(
        lambda: {
            "n": 0,
            "valid": 0,
            "input": [],
            "reasoning": [],
            "answer": [],
            "output": [],
            "api_total": [],
        }
    )

    for result_path in sorted(deepseek_dir.glob("cells/*/results.jsonl")):
        with result_path.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                key = (deepseek_config(row), row["dataset"], row["method"], row["condition"])
                cell = cells[key]
                usage = row.get("usage", {})
                cell["n"] += 1
                cell["valid"] += row.get("parse_success") is True
                for target, source in (
                    ("input", "input_tokens"),
                    ("reasoning", "reasoning_tokens"),
                    ("answer", "answer_tokens"),
                    ("output", "api_completion_tokens"),
                    ("api_total", "total_tokens"),
                ):
                    if usage.get(source) is not None:
                        cell[target].append(float(usage[source]))

    for result_path in sorted(qwen_dir.glob("*.jsonl")):
        config = result_path.stem
        with result_path.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                if row.get("experiment_scope") != "main" or row.get("method") not in METHODS:
                    continue
                key = (config, row["dataset_id"], row["method"], row["condition"])
                cell = cells[key]
                reasoning = row.get("reasoning_content_token_length")
                answer = row.get("content_token_length")
                raw = row.get("content") or row.get("model_result") or ""
                parsed, _ = parse_output(raw, row["method"])
                cell["n"] += 1
                cell["valid"] += parsed is not None
                if reasoning is not None:
                    cell["reasoning"].append(float(reasoning))
                if answer is not None:
                    cell["answer"].append(float(answer))
                if reasoning is not None and answer is not None:
                    cell["output"].append(float(reasoning) + float(answer))

    output: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for key, cell in cells.items():
        output[key] = {
            "n": cell["n"],
            "format_valid_rate": cell["valid"] / cell["n"],
            **{name: mean(cell[name]) for name in ("input", "reasoning", "answer", "output", "api_total")},
        }
    expected = {
        (config, dataset, method, condition)
        for config in CONFIGURATIONS
        for dataset in DATASETS
        for method in METHODS
        for condition in CONDITIONS
    }
    missing = expected - set(output)
    if missing:
        raise RuntimeError(f"missing {len(missing)} token cells: {sorted(missing)[:3]}")
    return output


def effect_tables(
    dataset: str, configurations: tuple[str, ...], results: dict[str, Any]
) -> list[str]:
    lines = [
        "#### 无注入效果",
        "",
        "| 模型 / 推理模式 | 方法 | N | Accuracy | Precision | Recall | F1 | MCC | FPR |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for config in configurations:
        methods = results[config]["datasets"][dataset]["methods"]
        clean_by_method = {
            method: methods[method]["no_prompt_injection"] for method in METHODS
        }
        best = {
            name: optimum(
                [clean_by_method[method][name] for method in METHODS],
                maximize=name != "fpr",
            )
            for name in ("accuracy", "precision", "recall", "f1", "mcc", "fpr")
        }
        for method in METHODS:
            value = clean_by_method[method]
            lines.append(
                f"| {CONFIG_LABELS[config]} | {method.title()} | {value['n']} | "
                f"{emphasized(fmt_metric(value['accuracy']), value['accuracy'], best['accuracy'])} | "
                f"{emphasized(fmt_metric(value['precision']), value['precision'], best['precision'])} | "
                f"{emphasized(fmt_metric(value['recall']), value['recall'], best['recall'])} | "
                f"{emphasized(fmt_metric(value['f1']), value['f1'], best['f1'])} | "
                f"{emphasized(fmt_metric(value['mcc']), value['mcc'], best['mcc'])} | "
                f"{emphasized(fmt_metric(value['fpr']), value['fpr'], best['fpr'])} |"
            )

    lines += [
        "",
        "#### 注入效果",
        "",
        "| 模型 / 推理模式 | 方法 | 黑注入 N | 黑 Recall | 黑 FNR | 白注入 N | 白 FPR | 白 TNR | 注入合并 Accuracy | Precision | Recall | F1 | MCC |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for config in configurations:
        methods = results[config]["datasets"][dataset]["methods"]
        values_by_method = {
            method: {
                "black": methods[method]["attacked_phishing"],
                "white": methods[method]["injected_legitimate_control"],
                "combined": methods[method]["prompt_injection"],
            }
            for method in METHODS
        }
        best = {
            "black_recall": optimum(
                [values_by_method[method]["black"]["recall"] for method in METHODS], True
            ),
            "black_fnr": optimum(
                [1 - values_by_method[method]["black"]["recall"] for method in METHODS], False
            ),
            "white_fpr": optimum(
                [values_by_method[method]["white"]["fpr"] for method in METHODS], False
            ),
            "white_tnr": optimum(
                [1 - values_by_method[method]["white"]["fpr"] for method in METHODS], True
            ),
            **{
                f"combined_{name}": optimum(
                    [values_by_method[method]["combined"][name] for method in METHODS], True
                )
                for name in ("accuracy", "precision", "recall", "f1", "mcc")
            },
        }
        for method in METHODS:
            black = values_by_method[method]["black"]
            white = values_by_method[method]["white"]
            combined = values_by_method[method]["combined"]
            black_fnr = None if black["recall"] is None else 1 - black["recall"]
            white_tnr = None if white["fpr"] is None else 1 - white["fpr"]
            lines.append(
                f"| {CONFIG_LABELS[config]} | {method.title()} | {black['n']} | "
                f"{emphasized(fmt_metric(black['recall']), black['recall'], best['black_recall'])} | "
                f"{emphasized(fmt_metric(black_fnr), black_fnr, best['black_fnr'])} | {white['n']} | "
                f"{emphasized(fmt_metric(white['fpr']), white['fpr'], best['white_fpr'])} | "
                f"{emphasized(fmt_metric(white_tnr), white_tnr, best['white_tnr'])} | "
                f"{emphasized(fmt_metric(combined['accuracy']), combined['accuracy'], best['combined_accuracy'])} | "
                f"{emphasized(fmt_metric(combined['precision']), combined['precision'], best['combined_precision'])} | "
                f"{emphasized(fmt_metric(combined['recall']), combined['recall'], best['combined_recall'])} | "
                f"{emphasized(fmt_metric(combined['f1']), combined['f1'], best['combined_f1'])} | "
                f"{emphasized(fmt_metric(combined['mcc']), combined['mcc'], best['combined_mcc'])} |"
            )
    lines += [
        "",
        "#### Ours 相对 Robust 的增量与注入检测",
        "",
        "注入检测指标同时使用无注入、黑注入和白注入样本；正类表示邮件中存在 prompt injection。",
        "",
        "| 模型 / 推理模式 | 黑 Recall 增量 | McNemar p | 注入合并 Accuracy 增量 | McNemar p | 注入检测 Precision | Recall | F1 | MCC |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for config in configurations:
        dataset_result = results[config]["datasets"][dataset]
        comparison = dataset_result["ours_vs_robust"]
        detection = dataset_result["ours_injection_detection"]
        lines.append(
            f"| {CONFIG_LABELS[config]} | {comparison['attacked_recall_delta_pp']:+.2f}pp | "
            f"{comparison['attacked_exact_mcnemar_p']:.3g} | "
            f"{comparison['prompt_injection_accuracy_delta_pp']:+.2f}pp | "
            f"{comparison['prompt_injection_exact_mcnemar_p']:.3g} | "
            f"{fmt_metric(detection['precision'])} | {fmt_metric(detection['recall'])} | "
            f"{fmt_metric(detection['f1'])} | {fmt_metric(detection['mcc'])} |"
        )
    return lines


def token_table(
    dataset: str,
    configurations: tuple[str, ...],
    tokens: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[str]:
    lines = [
        "",
        "#### 分条件 Token 与格式可靠性",
        "",
        "下列 token 均为每封邮件的平均值。Output = reasoning + 最终答案；API 总量 = input + API completion。",
        "",
        "| 模型 / 推理模式 | 方法 | 环境 | N | Input | Reasoning | Answer | Output | API 总量 | 格式有效率 |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for config in configurations:
        for method in METHODS:
            for condition in CONDITIONS:
                value = tokens[(config, dataset, method, condition)]
                peers = [tokens[(config, dataset, peer, condition)] for peer in METHODS]
                best = {
                    name: optimum([peer[name] for peer in peers], False)
                    for name in ("input", "reasoning", "answer", "output", "api_total")
                }
                best["format_valid_rate"] = optimum(
                    [peer["format_valid_rate"] for peer in peers], True
                )
                lines.append(
                    f"| {CONFIG_LABELS[config]} | {method.title()} | {CONDITION_LABELS[condition]} | "
                    f"{value['n']} | {emphasized(fmt_token(value['input']), value['input'], best['input'])} | "
                    f"{emphasized(fmt_token(value['reasoning']), value['reasoning'], best['reasoning'])} | "
                    f"{emphasized(fmt_token(value['answer']), value['answer'], best['answer'])} | "
                    f"{emphasized(fmt_token(value['output']), value['output'], best['output'])} | "
                    f"{emphasized(fmt_token(value['api_total']), value['api_total'], best['api_total'])} | "
                    f"{emphasized(fmt_percent(value['format_valid_rate']), value['format_valid_rate'], best['format_valid_rate'])} |"
                )
    return lines


def combined_table(
    dataset: str,
    configurations: tuple[str, ...],
    results: dict[str, Any],
    tokens: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[str]:
    """Put every metric for one dataset/model combination in a single table."""
    lines = [
        "| 推理模式 | 方法 | 无注入效果 | 黑注入效果 | 白注入效果 | 注入合并效果 | 无注入 Token / 格式 | 黑注入 Token / 格式 | 白注入 Token / 格式 | Ours 增量 / 注入检测 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for config in configurations:
        dataset_result = results[config]["datasets"][dataset]
        methods = dataset_result["methods"]
        values = {
            method: {
                "clean": methods[method]["no_prompt_injection"],
                "black": methods[method]["attacked_phishing"],
                "white": methods[method]["injected_legitimate_control"],
                "combined": methods[method]["prompt_injection"],
            }
            for method in METHODS
        }
        best: dict[str, float | None] = {}
        for environment in ("clean", "combined"):
            for name in ("accuracy", "precision", "recall", "f1", "mcc", "fpr"):
                best[f"{environment}_{name}"] = optimum(
                    [values[method][environment][name] for method in METHODS],
                    maximize=name != "fpr",
                )
        best["black_recall"] = optimum(
            [values[method]["black"]["recall"] for method in METHODS], True
        )
        best["white_fpr"] = optimum(
            [values[method]["white"]["fpr"] for method in METHODS], False
        )

        token_best: dict[tuple[str, str], float | None] = {}
        for condition in CONDITIONS:
            peers = [tokens[(config, dataset, method, condition)] for method in METHODS]
            for name in ("input", "reasoning", "answer", "output", "api_total"):
                token_best[(condition, name)] = optimum(
                    [peer[name] for peer in peers], False
                )
            token_best[(condition, "format_valid_rate")] = optimum(
                [peer["format_valid_rate"] for peer in peers], True
            )

        for method in METHODS:
            clean = values[method]["clean"]
            black = values[method]["black"]
            white = values[method]["white"]
            combined = values[method]["combined"]

            def metric(name: str, value: float | None, best_key: str) -> str:
                return f"{name}={emphasized(fmt_metric(value), value, best[best_key])}"

            def complements(value: dict[str, Any]) -> tuple[float | None, float | None]:
                fnr = None if value["recall"] is None else 1 - value["recall"]
                tnr = None if value["fpr"] is None else 1 - value["fpr"]
                return fnr, tnr

            clean_fnr, clean_tnr = complements(clean)
            combined_fnr, combined_tnr = complements(combined)
            black_fnr = None if black["recall"] is None else 1 - black["recall"]
            white_tnr = None if white["fpr"] is None else 1 - white["fpr"]

            clean_cell = "<br>".join(
                (
                    f"N={clean['n']}",
                    " / ".join(
                        metric(label, clean[key], f"clean_{key}")
                        for label, key in (
                            ("Acc", "accuracy"), ("P", "precision"),
                            ("R", "recall"), ("F1", "f1"),
                            ("MCC", "mcc"), ("FPR", "fpr"),
                        )
                    ),
                    f"FNR={emphasized(fmt_metric(clean_fnr), clean_fnr, None if best['clean_recall'] is None else 1 - best['clean_recall'])} / "
                    f"TNR={emphasized(fmt_metric(clean_tnr), clean_tnr, None if best['clean_fpr'] is None else 1 - best['clean_fpr'])}",
                )
            )
            black_cell = (
                f"N={black['n']}<br>"
                f"R={emphasized(fmt_metric(black['recall']), black['recall'], best['black_recall'])} / "
                f"FNR={emphasized(fmt_metric(black_fnr), black_fnr, None if best['black_recall'] is None else 1 - best['black_recall'])}"
            )
            white_cell = (
                f"N={white['n']}<br>"
                f"FPR={emphasized(fmt_metric(white['fpr']), white['fpr'], best['white_fpr'])} / "
                f"TNR={emphasized(fmt_metric(white_tnr), white_tnr, None if best['white_fpr'] is None else 1 - best['white_fpr'])}"
            )
            combined_cell = "<br>".join(
                (
                    f"N={combined['n']}",
                    " / ".join(
                        metric(label, combined[key], f"combined_{key}")
                        for label, key in (
                            ("Acc", "accuracy"), ("P", "precision"),
                            ("R", "recall"), ("F1", "f1"),
                            ("MCC", "mcc"), ("FPR", "fpr"),
                        )
                    ),
                    f"FNR={emphasized(fmt_metric(combined_fnr), combined_fnr, None if best['combined_recall'] is None else 1 - best['combined_recall'])} / "
                    f"TNR={emphasized(fmt_metric(combined_tnr), combined_tnr, None if best['combined_fpr'] is None else 1 - best['combined_fpr'])}",
                )
            )

            def token_cell(condition: str) -> str:
                value = tokens[(config, dataset, method, condition)]
                parts = " / ".join(
                    f"{label}={emphasized(fmt_token(value[name]), value[name], token_best[(condition, name)])}"
                    for label, name in (
                        ("I", "input"), ("R", "reasoning"), ("A", "answer"),
                        ("O", "output"), ("T", "api_total"),
                    )
                )
                valid = emphasized(
                    fmt_percent(value["format_valid_rate"]),
                    value["format_valid_rate"],
                    token_best[(condition, "format_valid_rate")],
                )
                return f"{parts}<br>Valid={valid}"

            ours_cell = "—"
            if method == "ours":
                comparison = dataset_result["ours_vs_robust"]
                detection = dataset_result["ours_injection_detection"]
                ours_cell = "<br>".join(
                    (
                        f"黑R Δ={comparison['attacked_recall_delta_pp']:+.2f}pp (p={comparison['attacked_exact_mcnemar_p']:.3g})",
                        f"注入Acc Δ={comparison['prompt_injection_accuracy_delta_pp']:+.2f}pp (p={comparison['prompt_injection_exact_mcnemar_p']:.3g})",
                        f"检测 P/R/F1/MCC={fmt_metric(detection['precision'])}/{fmt_metric(detection['recall'])}/{fmt_metric(detection['f1'])}/{fmt_metric(detection['mcc'])}",
                    )
                )

            lines.append(
                f"| {results[config]['mode']} | {method.title()} | {clean_cell} | "
                f"{black_cell} | {white_cell} | {combined_cell} | "
                f"{token_cell('clean')} | {token_cell('attacked_phishing')} | "
                f"{token_cell('injected_legitimate_control')} | {ours_cell} |"
            )
    return lines


def html_value(text: str, value: float | None, best: float | None) -> str:
    rendered = emphasized(text, value, best)
    if rendered.startswith("**") and rendered.endswith("**"):
        return f"<strong>{rendered[2:-2]}</strong>"
    return rendered


def combined_html_table(
    dataset: str,
    configurations: tuple[str, ...],
    results: dict[str, Any],
    tokens: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[str]:
    """Render one readable, grouped HTML table per dataset/model combination."""
    lines = [
        '<div style="overflow-x:auto">',
        '<table style="font-size:0.82em; white-space:nowrap">',
        "<thead>",
        "<tr><th rowspan=\"2\">推理模式</th><th rowspan=\"2\">方法</th><th rowspan=\"2\">环境</th><th rowspan=\"2\">N</th><th colspan=\"8\">分类效果</th><th colspan=\"6\">平均 Token / 可靠性</th><th rowspan=\"2\">Ours 增量 / 注入检测</th></tr>",
        "<tr><th>Acc</th><th>P</th><th>R</th><th>F1</th><th>MCC</th><th>FPR</th><th>FNR</th><th>TNR</th><th>I</th><th>Rsn</th><th>A</th><th>O</th><th>T</th><th>Valid</th></tr>",
        "</thead>",
        "<tbody>",
    ]
    environments = (
        ("clean", "无注入", "clean"),
        ("black", "黑注入", "attacked_phishing"),
        ("white", "白注入", "injected_legitimate_control"),
        ("combined", "注入合并", None),
    )
    for config in configurations:
        dataset_result = results[config]["datasets"][dataset]
        methods = dataset_result["methods"]
        values = {
            method: {
                "clean": methods[method]["no_prompt_injection"],
                "black": methods[method]["attacked_phishing"],
                "white": methods[method]["injected_legitimate_control"],
                "combined": methods[method]["prompt_injection"],
            }
            for method in METHODS
        }
        effect_best: dict[tuple[str, str], float | None] = {}
        for environment in ("clean", "combined"):
            for name in ("accuracy", "precision", "recall", "f1", "mcc", "fpr"):
                effect_best[(environment, name)] = optimum(
                    [values[method][environment][name] for method in METHODS],
                    maximize=name != "fpr",
                )
        effect_best[("black", "recall")] = optimum(
            [values[method]["black"]["recall"] for method in METHODS], True
        )
        effect_best[("white", "fpr")] = optimum(
            [values[method]["white"]["fpr"] for method in METHODS], False
        )
        token_best: dict[tuple[str, str], float | None] = {}
        for _, _, condition in environments[:3]:
            assert condition is not None
            peers = [tokens[(config, dataset, method, condition)] for method in METHODS]
            for name in ("input", "reasoning", "answer", "output", "api_total"):
                token_best[(condition, name)] = optimum(
                    [peer[name] for peer in peers], False
                )
            token_best[(condition, "format_valid_rate")] = optimum(
                [peer["format_valid_rate"] for peer in peers], True
            )

        for method_index, method in enumerate(METHODS):
            for environment_index, (environment, label, condition) in enumerate(environments):
                value = values[method][environment]
                row = ["<tr>"]
                if method_index == 0 and environment_index == 0:
                    row.append(f'<th rowspan="12">{results[config]["mode"]}</th>')
                if environment_index == 0:
                    row.append(f'<th rowspan="4">{method.title()}</th>')
                row.extend((f"<td>{label}</td>", f"<td>{value['n']}</td>"))

                shown: dict[str, float | None] = {
                    name: value.get(name)
                    for name in ("accuracy", "precision", "recall", "f1", "mcc", "fpr")
                }
                if environment == "black":
                    shown = {name: None for name in shown}
                    shown["recall"] = value["recall"]
                elif environment == "white":
                    shown = {name: None for name in shown}
                    shown["fpr"] = value["fpr"]
                shown["fnr"] = None if shown["recall"] is None else 1 - shown["recall"]
                shown["tnr"] = None if shown["fpr"] is None else 1 - shown["fpr"]

                for name in ("accuracy", "precision", "recall", "f1", "mcc", "fpr", "fnr", "tnr"):
                    metric_value = shown[name]
                    if name == "fnr":
                        recall_best = effect_best.get((environment, "recall"))
                        best_value = None if recall_best is None else 1 - recall_best
                    elif name == "tnr":
                        fpr_best = effect_best.get((environment, "fpr"))
                        best_value = None if fpr_best is None else 1 - fpr_best
                    else:
                        best_value = effect_best.get((environment, name))
                    row.append(f"<td>{html_value(fmt_metric(metric_value), metric_value, best_value)}</td>")

                if condition is None:
                    row.extend("<td>—</td>" for _ in range(6))
                else:
                    token_value = tokens[(config, dataset, method, condition)]
                    for name in ("input", "reasoning", "answer", "output", "api_total"):
                        row.append(
                            f"<td>{html_value(fmt_token(token_value[name]), token_value[name], token_best[(condition, name)])}</td>"
                        )
                    row.append(
                        f"<td>{html_value(fmt_percent(token_value['format_valid_rate']), token_value['format_valid_rate'], token_best[(condition, 'format_valid_rate')])}</td>"
                    )

                evidence = "—"
                if method == "ours" and environment == "black":
                    comparison = dataset_result["ours_vs_robust"]
                    evidence = (
                        f"R Δ={comparison['attacked_recall_delta_pp']:+.2f}pp; "
                        f"p={comparison['attacked_exact_mcnemar_p']:.3g}"
                    )
                elif method == "ours" and environment == "combined":
                    comparison = dataset_result["ours_vs_robust"]
                    detection = dataset_result["ours_injection_detection"]
                    evidence = (
                        f"Acc Δ={comparison['prompt_injection_accuracy_delta_pp']:+.2f}pp; "
                        f"p={comparison['prompt_injection_exact_mcnemar_p']:.3g}<br>"
                        f"检测 P/R/F1/MCC={fmt_metric(detection['precision'])}/"
                        f"{fmt_metric(detection['recall'])}/{fmt_metric(detection['f1'])}/"
                        f"{fmt_metric(detection['mcc'])}"
                    )
                row.extend((f"<td>{evidence}</td>", "</tr>"))
                lines.append("".join(row))
    lines.extend(("</tbody>", "</table>", "</div>"))
    return environment_first_html_table(lines)


def environment_first_html_table(lines: list[str]) -> list[str]:
    """Reorder a rendered table to environment, then mode, then method."""
    records: dict[tuple[str, str, str], list[str]] = {}
    current_mode = current_method = ""
    for line in lines:
        if not line.startswith("<tr>") or "<td>" not in line:
            continue
        cells = re.findall(r"<(?:th|td)[^>]*>(.*?)</(?:th|td)>", line)
        if len(cells) == 19:
            current_mode, current_method = cells[0], cells[1]
            cells = cells[2:]
        elif len(cells) == 18:
            current_method = cells[0]
            cells = cells[1:]
        environment = cells[0]
        records[(environment, current_mode, current_method)] = cells[1:]

    output = [
        '<div style="overflow-x:auto">',
        '<table style="font-size:0.82em; white-space:nowrap">',
        "<thead>",
        "<tr><th rowspan=\"2\">环境</th><th rowspan=\"2\">推理模式</th><th rowspan=\"2\">方法</th><th rowspan=\"2\">N</th><th colspan=\"8\">分类效果</th><th colspan=\"6\">平均 Token / 可靠性</th><th rowspan=\"2\">Ours 增量 / 注入检测</th></tr>",
        "<tr><th>Acc</th><th>P</th><th>R</th><th>F1</th><th>MCC</th><th>FPR</th><th>FNR</th><th>TNR</th><th>I</th><th>Rsn</th><th>A</th><th>O</th><th>T</th><th>Valid</th></tr>",
        "</thead>",
        "<tbody>",
    ]
    for environment in ("无注入", "黑注入", "白注入", "注入合并"):
        for mode_index, mode in enumerate(("non-thinking", "thinking")):
            for method_index, method in enumerate(("Direct", "Robust", "Ours")):
                row = ["<tr>"]
                if mode_index == 0 and method_index == 0:
                    row.append(f'<th rowspan="6">{environment}</th>')
                if method_index == 0:
                    row.append(f'<th rowspan="3">{mode}</th>')
                row.append(f"<th>{method}</th>")
                row.extend(f"<td>{value}</td>" for value in records[(environment, mode, method)])
                row.append("</tr>")
                output.append("".join(row))
    output.extend(("</tbody>", "</table>", "</div>"))
    return output


def latex_escape(value: str) -> str:
    value = value.replace("<strong>", r"\textbf{").replace("</strong>", "}")
    value = value.replace("<br>", "; ").replace("—", "--")
    value = value.replace("%", r"\%").replace("_", r"\_").replace("&", r"\&")
    return value


def latex_document(markdown_lines: list[str]) -> str:
    """Convert the generated HTML tables into a standalone XeLaTeX document."""
    output = [
        r"\documentclass{article}",
        r"\usepackage{fontspec}",
        r"\setmainfont{Noto Sans CJK SC}[BoldFont=Noto Sans CJK SC Bold]",
        r"\usepackage{booktabs,multirow,graphicx,rotating}",
        r"\begin{document}",
    ]
    dataset = model = ""
    index = 0
    while index < len(markdown_lines):
        line = markdown_lines[index]
        if line.startswith("## ") and line != "## 口径" and line != "## 数据来源":
            dataset = line[3:]
        elif line.startswith("### "):
            model = line[4:]
        elif line.startswith("<table"):
            rows: list[str] = []
            index += 1
            while index < len(markdown_lines) and markdown_lines[index] != "</table>":
                html_row = markdown_lines[index]
                if html_row.startswith("<tr>") and "rowspan=\"2\"" not in html_row and "colspan=\"" not in html_row:
                    cells = re.findall(r"<(?:th|td)([^>]*)>(.*?)</(?:th|td)>", html_row)
                    if cells:
                        rendered: list[str] = []
                        for attributes, content in cells:
                            match = re.search(r'rowspan="(\d+)"', attributes)
                            escaped = latex_escape(content)
                            rendered.append(
                                rf"\multirow{{{match.group(1)}}}{{*}}{{{escaped}}}"
                                if match
                                else escaped
                            )
                        if len(rendered) == 18:
                            rendered.insert(0, "")
                        elif len(rendered) == 17:
                            rendered[0:0] = ("", "")
                        if len(rendered) == 19:
                            rows.append(" & ".join(rendered) + r" \\")
                index += 1
            caption = latex_escape(f"{dataset} × {model} 全指标对比")
            output += [
                r"\begin{sidewaystable*}[p]",
                r"\centering\tiny",
                rf"\caption{{{caption}}}",
                r"\resizebox{\textheight}{!}{%",
                r"\begin{tabular}{lllrrrrrrrrrrrrrrrp{5cm}}",
                r"\toprule",
                r"环境 & 推理模式 & 方法 & N & \multicolumn{8}{c}{分类效果} & \multicolumn{6}{c}{平均 Token / 可靠性} & Ours 增量 / 注入检测 \\",
                r"\cmidrule(lr){5-12}\cmidrule(lr){13-18}",
                r" & & & & Acc & P & R & F1 & MCC & FPR & FNR & TNR & I & Rsn & A & O & T & Valid & \\",
                r"\midrule",
                *rows,
                r"\bottomrule",
                r"\end{tabular}%",
                r"}",
                r"\end{sidewaystable*}",
            ]
        index += 1
    output.append(r"\end{document}")
    return "\n".join(output) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--deepseek-raw-dir", type=Path, required=True)
    parser.add_argument("--qwen-raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--latex-output", type=Path)
    args = parser.parse_args()

    aggregate = json.loads(args.results.read_text(encoding="utf-8"))
    tokens = collect_token_stats(args.deepseek_raw_dir, args.qwen_raw_dir)
    lines = [
        "# 全量实验：数据集 × 模型 × 推理模式 × 注入条件详细对比",
        "",
        "## 口径",
        "",
        "- **无注入**：clean phishing 与 clean legitimate 合并，报告完整二分类指标。",
        "- **黑注入**：向 phishing 插入攻击指令，全部为正类，核心指标为 Recall/FNR。",
        "- **白注入**：向 legitimate 插入同分布攻击指令，全部为负类，核心指标为 FPR/TNR。",
        "- **注入合并**：黑注入与白注入合并成平衡二分类集合，报告 Accuracy、Precision、Recall、F1、MCC。",
        "- 分类指标采用解析失败计为分类错误的保守口径。摘要超过 100 字符只作软检查，不视为格式失败。",
        "- DeepSeek 原始响应记录 input、reasoning、answer、API completion 和 total token；Qwen/vLLM 原始结果只记录 reasoning 与 answer token，因此 Input 和 API 总量标为 `—`。",
        "- 每个数据集与模型组合只使用一张综合表；Token 按实际条件分别统计，不是跨条件平均。",
        "- Token 缩写：I=input、R=reasoning、A=answer、O=reasoning+answer、T=API total；Valid=格式有效率。",
        "- **粗体表示同一数据集、模型、推理模式和环境下 Direct/Robust/Ours 的最优值；并列最优同时加粗。效果指标除 FPR/FNR 外越高越好，FPR/FNR 和 token 越低越好。**",
        "",
    ]
    for dataset in DATASETS:
        lines += [f"## {DATASET_LABELS[dataset]}", ""]
        for model_label, configurations in MODEL_GROUPS:
            lines += [f"### {model_label}", ""]
            lines += combined_html_table(
                dataset, configurations, aggregate["results"], tokens
            )
            lines.append("")
    lines += [
        "## 数据来源",
        "",
        f"- 效果指标：`{args.results}`",
        f"- DeepSeek 原始结果：`{args.deepseek_raw_dir}`",
        f"- Qwen 原始结果：`{args.qwen_raw_dir}`",
        "- 生成脚本：`src/tools/evaluation/build_detailed_comparison.py`",
        "",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    if args.latex_output is not None:
        args.latex_output.parent.mkdir(parents=True, exist_ok=True)
        args.latex_output.write_text(latex_document(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "latex_output": None if args.latex_output is None else str(args.latex_output),
                "token_cells": len(tokens),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
