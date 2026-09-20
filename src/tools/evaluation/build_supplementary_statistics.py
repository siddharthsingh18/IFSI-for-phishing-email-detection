#!/usr/bin/env python3
"""Build paired-flip, multiplicity, token, and reliability supplements from raw JSONL."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from phishbench.evaluate import conservative_prediction, exact_mcnemar, percentile, reparse_result
from phishbench.io import read_jsonl, write_json
from phishbench.runner import parse_output


DATASET_NAMES = {
    "phishfuzzer_seed_42": "PhishFuzzer",
    "nazario_enron_quality_seed_42": "Nazario+Enron",
}
METHOD_NAMES = {"direct": "Direct", "robust": "Robust", "ours": "Ours"}
CONFIG_ORDER = (
    "deepseek-v4-flash_non-thinking",
    "deepseek-v4-flash_thinking",
    "deepseek-v4-pro_non-thinking",
    "deepseek-v4-pro_thinking",
    "qwen3.5-9b_non-thinking",
    "qwen3.5-9b_thinking",
    "qwen3.5-35b-a3b_non-thinking",
    "qwen3.5-35b-a3b_thinking",
)


def normalize_deepseek(paths: Iterable[Path]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for path in paths:
        for index, source in enumerate(read_jsonl(path)):
            key = str(source.get("run_item_id") or f"{path}:{index}")
            source = reparse_result(source)
            mode = "thinking" if source["thinking"] == "on" else "non-thinking"
            usage = source.get("usage") or {}
            latest[key] = {
                "config": f"{source['model_requested']}_{mode}",
                "dataset": source["dataset"],
                "condition": source["condition"],
                "method": source["method"],
                "original_id": str(source.get("original_id") or source["email_id"]),
                "label": int(source["label"]),
                "prediction": source.get("prediction"),
                "parse_success": bool(source.get("parse_success")),
                "request_success": bool(source.get("request_success")),
                "finish_reason": source.get("finish_reason"),
                "attempt_count": source.get("attempt_count"),
                "input_tokens": usage.get("input_tokens"),
                "reasoning_tokens": usage.get("reasoning_tokens"),
                "answer_tokens": usage.get("answer_tokens"),
                "output_tokens": usage.get("api_completion_tokens")
                if usage.get("api_completion_tokens") is not None
                else usage.get("generated_tokens_including_reasoning"),
                "total_tokens": usage.get("total_tokens"),
                "latency_ms": source.get("latency_ms"),
            }
    return list(latest.values())


def normalize_qwen(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        for source in read_jsonl(path):
            if source.get("experiment_scope") != "main" or source.get("method") not in METHOD_NAMES:
                continue
            method = str(source["method"])
            raw = source.get("content") or source.get("model_result") or ""
            parsed, _ = parse_output(raw, method)
            truth = source["ground_truth_do_not_send_to_model"]
            answer = source.get("content_token_length")
            reasoning = source.get("reasoning_content_token_length")
            rows.append(
                {
                    "config": path.stem,
                    "dataset": source["dataset_id"],
                    "condition": source["condition"],
                    "method": method,
                    "original_id": str(source["original_id"]),
                    "label": int(truth["label"]),
                    "prediction": None if parsed is None else int(parsed["is_phishing"]),
                    "parse_success": parsed is not None,
                    "request_success": None,
                    "finish_reason": source.get("finish_reason"),
                    "attempt_count": None,
                    "input_tokens": None,
                    "reasoning_tokens": reasoning,
                    "answer_tokens": answer,
                    "output_tokens": None
                    if answer is None or reasoning is None
                    else float(answer) + float(reasoning),
                    "total_tokens": None,
                    "latency_ms": None,
                }
            )
    return rows


def summary(values: list[float]) -> dict[str, float | None]:
    return {
        "mean": statistics.fmean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "p95": percentile(values, 0.95),
    }


def exact_p(a_correct_b_wrong: int, a_wrong_b_correct: int) -> float:
    n = a_correct_b_wrong + a_wrong_b_correct
    if not n:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(a_correct_b_wrong, a_wrong_b_correct) + 1)) / 2**n
    return min(1.0, 2 * tail)


def holm_adjust(items: list[tuple[str, float]]) -> dict[str, float]:
    ordered = sorted(items, key=lambda item: item[1])
    adjusted: dict[str, float] = {}
    running = 0.0
    total = len(ordered)
    for rank, (key, p_value) in enumerate(ordered):
        running = max(running, min(1.0, (total - rank) * p_value))
        adjusted[key] = running
    return adjusted


def build(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["config"], row["dataset"], row["method"], row["condition"])].append(row)

    flips: list[dict[str, Any]] = []
    for config in CONFIG_ORDER:
        for dataset in DATASET_NAMES:
            for method in METHOD_NAMES:
                clean = {
                    row["original_id"]: row
                    for row in grouped.get((config, dataset, method, "clean"), [])
                }
                for condition in ("attacked_phishing", "injected_legitimate_control"):
                    altered = grouped.get((config, dataset, method, condition), [])
                    pairs = [(clean[row["original_id"]], row) for row in altered if row["original_id"] in clean]
                    harmful = sum(
                        conservative_prediction(a) == a["label"]
                        and conservative_prediction(b) != b["label"]
                        for a, b in pairs
                    )
                    helpful = sum(
                        conservative_prediction(a) != a["label"]
                        and conservative_prediction(b) == b["label"]
                        for a, b in pairs
                    )
                    flips.append(
                        {
                            "config": config,
                            "dataset": dataset,
                            "method": method,
                            "condition": condition,
                            "paired_n": len(pairs),
                            "harmful_count": harmful,
                            "harmful_rate": harmful / len(pairs) if pairs else None,
                            "helpful_count": helpful,
                            "helpful_rate": helpful / len(pairs) if pairs else None,
                            "net_harmful_count": harmful - helpful,
                        }
                    )

    tests: list[dict[str, Any]] = []
    raw_ps: list[tuple[str, float]] = []
    for config in CONFIG_ORDER:
        for dataset in DATASET_NAMES:
            robust = grouped.get((config, dataset, "robust", "attacked_phishing"), [])
            ours = grouped.get((config, dataset, "ours", "attacked_phishing"), [])
            result = exact_mcnemar(robust, ours)
            key = f"{config}|{dataset}"
            robust_correct_ours_wrong = int(result["a_correct_b_wrong"])
            robust_wrong_ours_correct = int(result["a_wrong_b_correct"])
            p_value = exact_p(robust_correct_ours_wrong, robust_wrong_ours_correct)
            raw_ps.append((key, p_value))
            tests.append(
                {
                    "key": key,
                    "config": config,
                    "dataset": dataset,
                    "robust_correct_ours_wrong": robust_correct_ours_wrong,
                    "robust_wrong_ours_correct": robust_wrong_ours_correct,
                    "net_ours_recoveries": robust_wrong_ours_correct - robust_correct_ours_wrong,
                    "raw_p": p_value,
                }
            )
    adjusted = holm_adjust(raw_ps)
    for test in tests:
        test["holm_p_16"] = adjusted[test["key"]]
        test["holm_significant_0_05"] = adjusted[test["key"]] < 0.05

    efficiency: list[dict[str, Any]] = []
    reliability: list[dict[str, Any]] = []
    by_config_method: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_config_method[(row["config"], row["method"])].append(row)
    for config in CONFIG_ORDER:
        for method in METHOD_NAMES:
            values = by_config_method[(config, method)]
            efficiency.append(
                {
                    "config": config,
                    "method": method,
                    **{
                        field: summary(
                            [float(row[field]) for row in values if row.get(field) is not None]
                        )
                        for field in (
                            "input_tokens",
                            "reasoning_tokens",
                            "answer_tokens",
                            "output_tokens",
                            "total_tokens",
                            "latency_ms",
                        )
                    },
                }
            )
            finish = Counter(str(row.get("finish_reason")) for row in values)
            attempts = [int(row["attempt_count"]) for row in values if row.get("attempt_count") is not None]
            request_known = [row for row in values if row.get("request_success") is not None]
            reliability.append(
                {
                    "config": config,
                    "method": method,
                    "records": len(values),
                    "request_success_rate": None
                    if not request_known
                    else sum(row["request_success"] is True for row in request_known) / len(request_known),
                    "format_valid_rate": sum(row["parse_success"] for row in values) / len(values),
                    "invalid_outputs": sum(not row["parse_success"] for row in values),
                    "finish_reasons": dict(finish),
                    "retried_records": sum(value > 1 for value in attempts),
                    "max_attempt_count": max(attempts) if attempts else None,
                }
            )

    return {
        "format": "phishbench-supplementary-statistics-v1",
        "scope": {
            "primary_paper_models": ["deepseek-v4-pro", "qwen3.5-9b", "qwen3.5-35b-a3b"],
            "archival_boundary_model": "deepseek-v4-flash",
            "holm_family": "16 Ours-vs-Robust attacked-phishing comparisons",
            "token_cost_proxy": "output tokens including reasoning; Qwen input/latency unavailable",
        },
        "paired_clean_to_injected_flips": flips,
        "ours_vs_robust_attacked_mcnemar": tests,
        "token_distributions": efficiency,
        "reliability": reliability,
    }


def pct(value: float | None) -> str:
    return "—" if value is None else f"{100 * value:.2f}%"


def num(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f}"


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# 补充统计：配对翻转、多重校正、Token 与可靠性",
        "",
        "口径：论文主叙事暂以 DeepSeek-v4-Pro、Qwen3.5-9B、Qwen3.5-35B-A3B 为主；",
        "DeepSeek-v4-Flash 原始结果继续保留，作为审计与方法边界，不进入主张汇总。",
        "成本代理统一使用最终回答加 reasoning 的输出 Token；Qwen 原始记录没有统一 input token 和 latency。",
        "",
        "## Ours 的 Clean→Attack 配对翻转",
        "",
        "`损害`表示 clean 判对、注入后判错；`恢复`表示 clean 判错、注入后判对。",
        "",
        "| 配置 | 数据集 | 条件 | N | 损害 | 恢复 | 净损害 |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in report["paired_clean_to_injected_flips"]:
        if row["method"] != "ours" or row["config"].startswith("deepseek-v4-flash"):
            continue
        condition = "黑注入 phishing" if row["condition"] == "attacked_phishing" else "白注入 legitimate"
        lines.append(
            f"| {row['config']} | {DATASET_NAMES[row['dataset']]} | {condition} | {row['paired_n']} | "
            f"{row['harmful_count']} ({pct(row['harmful_rate'])}) | {row['helpful_count']} ({pct(row['helpful_rate'])}) | "
            f"{row['net_harmful_count']:+d} |"
        )

    lines += [
        "",
        "## Ours vs Robust：attacked-phishing McNemar 与 Holm 校正",
        "",
        "Holm family 包含完整矩阵 16 个比较，包括归档的 Flash，因而是较保守的校正。",
        "`R错/O对`是 Ours 相对 Robust 恢复的样本；`R对/O错`是 Ours 新增漏检。",
        "",
        "| 配置 | 数据集 | R错/O对 | R对/O错 | 净恢复 | 原始 p | Holm p | 0.05 |",
        "|---|---|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in report["ours_vs_robust_attacked_mcnemar"]:
        lines.append(
            f"| {row['config']} | {DATASET_NAMES[row['dataset']]} | {row['robust_wrong_ours_correct']} | "
            f"{row['robust_correct_ours_wrong']} | {row['net_ours_recoveries']:+d} | {row['raw_p']:.3g} | "
            f"{row['holm_p_16']:.3g} | {'是' if row['holm_significant_0_05'] else '否'} |"
        )

    lines += [
        "",
        "## Token 分布",
        "",
        "每项为 `mean / median / p95`；在两个数据集和三种条件上汇总。",
        "",
        "| 配置 | 方法 | Answer | Reasoning | 输出合计 | Input | Total |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["token_distributions"]:
        if row["config"].startswith("deepseek-v4-flash"):
            continue
        def triple(field: str) -> str:
            value = row[field]
            return f"{num(value['mean'])}/{num(value['median'])}/{num(value['p95'])}"
        lines.append(
            f"| {row['config']} | {METHOD_NAMES[row['method']]} | {triple('answer_tokens')} | "
            f"{triple('reasoning_tokens')} | {triple('output_tokens')} | {triple('input_tokens')} | {triple('total_tokens')} |"
        )

    lines += [
        "",
        "## 可靠性与失败",
        "",
        "失败记录没有从分类分母静默删除；分类统计对不可解析结果采用保守错误计分。",
        "Qwen 本地结果未记录逐请求 API 成功字段，因此该列为 `—`，但所有冻结 prompt 均有返回记录。",
        "",
        "| 配置 | 方法 | 记录数 | 请求成功率 | 格式有效率 | 无效输出 | 重试记录 | 最大尝试次数 | Finish reason |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["reliability"]:
        if row["config"].startswith("deepseek-v4-flash"):
            continue
        finishes = ", ".join(f"{key}:{value}" for key, value in sorted(row["finish_reasons"].items()))
        lines.append(
            f"| {row['config']} | {METHOD_NAMES[row['method']]} | {row['records']} | "
            f"{pct(row['request_success_rate'])} | {pct(row['format_valid_rate'])} | {row['invalid_outputs']} | "
            f"{row['retried_records']} | {row['max_attempt_count'] or '—'} | {finishes} |"
        )
    lines += [
        "",
        "## 可复现性说明",
        "",
        "本报告完全由保留的逐请求 JSONL 重建，没有重新调用任何模型服务。机器可读完整结果包含 Flash 和全部方法。",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deepseek-cells", type=Path, required=True)
    parser.add_argument("--qwen-dir", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    deepseek_paths = sorted(args.deepseek_cells.glob("*/results.jsonl"))
    qwen_paths = sorted(args.qwen_dir.glob("*.jsonl"))
    rows = normalize_deepseek(deepseek_paths) + normalize_qwen(qwen_paths)
    report = build(rows)
    write_json(args.json_output, report)
    write_markdown(report, args.markdown_output)
    print(json.dumps({"rows": len(rows), "json": str(args.json_output), "markdown": str(args.markdown_output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
