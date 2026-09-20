"""Export frozen experiment prompts as a streamable, self-describing JSONL file."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from .io import read_jsonl, sha256_file, sha256_text, stable_id
from .prompts import PROMPT_VERSION, build_prompt, prompt_snapshot
from .runner import PARSER_VERSION


CONDITIONS = ("clean", "attacked_phishing", "injected_legitimate_control")


def result_schema(method: str) -> dict[str, str]:
    if method == "ours":
        return {
            "has_prompt_injection": "boolean",
            "prompt_injection_summary": "string|null",
            "is_phishing": "boolean",
        }
    if method == "ours_no_summary":
        return {"has_prompt_injection": "boolean", "is_phishing": "boolean"}
    return {"is_phishing": "boolean"}


def build_item(
    record: dict[str, Any],
    *,
    dataset: str,
    condition: str,
    method: str,
    experiment_scope: str,
    input_path: Path,
    input_sha256: str,
    record_index: int,
    label_rank: int,
    recommended_small_scale: bool,
) -> dict[str, Any]:
    prompt = build_prompt(record, method)
    email_id = str(record["email_id"])
    original_id = str(record.get("original_id") or email_id)
    prompt_id = stable_id(
        "portable-prompt-v1", dataset, condition, method, email_id, prompt.expanded_prompt_sha256, length=32
    )
    return {
        "prompt_id": prompt_id,
        "experiment_scope": experiment_scope,
        "dataset_id": dataset,
        "condition": condition,
        "method": method,
        "email_id": email_id,
        "original_id": original_id,
        "paired_base_original_id": original_id,
        "sample_pair_id": stable_id("sample-pair-v1", dataset, original_id, length=32),
        "record_index_in_input": record_index,
        "label_rank_in_input": label_rank,
        "recommended_small_scale_seed_42": recommended_small_scale,
        "source_trace": {
            "input_file": str(input_path),
            "input_file_sha256": input_sha256,
            "source_dataset": record.get("source_dataset"),
            "source_record_id": record.get("source_record_id"),
            "source_provenance": record.get("source_provenance"),
            "variant_type": record.get("variant_type"),
            "attack_family": record.get("attack_family"),
            "attack_template_id": record.get("attack_template_id"),
            "attack_position": record.get("attack_position"),
            "attack_seed": record.get("attack_seed"),
        },
        "prompt_trace": {
            "prompt_version": prompt.version,
            "expanded_prompt_sha256": prompt.expanded_prompt_sha256,
            "block_hashes": prompt.block_hashes,
        },
        "request": {
            "messages": prompt.messages,
            "response_format": {"type": "json_object"},
            "expected_output_schema": result_schema(method),
        },
        "ground_truth_do_not_send_to_model": {
            "label": int(record["label"]),
            "label_name": record.get("label_name"),
            "is_phishing": bool(int(record["label"])),
            "has_prompt_injection": bool(record.get("has_injected_prompt", condition != "clean")),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("experiments/config/main_matrix.json"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=Path("experiments/inputs/phishbench_portable_prompts_v1.jsonl"))
    parser.add_argument("--exclude-ablation", action="store_true")
    args = parser.parse_args()

    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    main_scopes = sorted({(cell["dataset"], cell["condition"], cell["method"]) for cell in matrix["cells"]})
    scopes = [("main", *scope) for scope in main_scopes]
    if not args.exclude_ablation:
        ablation = matrix["ablation"]
        scopes.extend(
            ("ablation", ablation["dataset"], condition, ablation["method"])
            for condition in ablation["conditions"]
        )

    datasets = sorted({dataset for _, dataset, _, _ in scopes})
    recommended_ids: dict[str, dict[int, set[str]]] = {}
    recommended_indices: dict[str, list[int]] = {}
    for dataset in datasets:
        attacked = read_jsonl(args.processed_dir / dataset / "attacked_phishing.jsonl")
        controls = read_jsonl(args.processed_dir / dataset / "injected_legitimate_control.jsonl")
        if len(attacked) != len(controls) or len(attacked) < 100:
            raise RuntimeError(f"cannot form paired 100-per-label portable subset for {dataset}")
        indices = sorted(random.Random(42).sample(range(len(attacked)), 100))
        recommended_indices[dataset] = indices
        recommended_ids[dataset] = {
            1: {str(attacked[index]["original_id"]) for index in indices},
            0: {str(controls[index]["original_id"]) for index in indices},
        }

    input_files: dict[str, dict[str, Any]] = {}
    prompts: list[dict[str, Any]] = []
    for experiment_scope, dataset, condition, method in scopes:
        input_path = args.processed_dir / dataset / f"{condition}.jsonl"
        input_sha256 = sha256_file(input_path)
        records = read_jsonl(input_path)
        input_files[str(input_path)] = {
            "sha256": input_sha256,
            "records": len(records),
        }
        label_counts = {0: 0, 1: 0}
        for record_index, record in enumerate(records):
            label = int(record["label"])
            label_rank = label_counts[label]
            label_counts[label] += 1
            prompts.append(
                build_item(
                    record,
                    dataset=dataset,
                    condition=condition,
                    method=method,
                    experiment_scope=experiment_scope,
                    input_path=input_path,
                    input_sha256=input_sha256,
                    record_index=record_index,
                    label_rank=label_rank,
                    recommended_small_scale=str(record.get("original_id") or record["email_id"])
                    in recommended_ids[dataset][label],
                )
            )

    prompt_ids = [item["prompt_id"] for item in prompts]
    if len(prompt_ids) != len(set(prompt_ids)):
        raise RuntimeError("portable prompt_id collision or duplicate scope")
    counts: dict[str, Any] = {
        "total_prompts": len(prompts),
        "by_scope": {},
        "by_dataset": {},
        "by_method": {},
        "by_condition": {},
        "recommended_small_scale_prompts": sum(
            bool(item["recommended_small_scale_seed_42"]) for item in prompts
        ),
    }
    for item in prompts:
        for key, field in (
            ("by_scope", "experiment_scope"),
            ("by_dataset", "dataset_id"),
            ("by_method", "method"),
            ("by_condition", "condition"),
        ):
            value = str(item[field])
            counts[key][value] = counts[key].get(value, 0) + 1

    manifest = {
        "_record_type": "manifest",
        "format_version": "phishbench-portable-prompts-jsonl-v1",
        "prompt_version": PROMPT_VERSION,
        "parser_version_for_later_analysis": PARSER_VERSION,
        "matrix": {
            "path": str(args.matrix),
            "sha256": sha256_file(args.matrix),
            "matrix_version": matrix["matrix_version"],
            "main_note": "Model and reasoning mode do not change messages, so each unique dataset/condition/method prompt is stored once.",
            "main_reference_models": sorted({cell["model"] for cell in matrix["cells"]}),
            "main_reference_thinking_modes": sorted({cell["thinking"] for cell in matrix["cells"]}),
            "ablation_included": not args.exclude_ablation,
        },
        "input_files": input_files,
        "counts": counts,
        "jsonl_layout": {
            "line_1": "manifest record with _record_type=manifest; do not send it to a model",
            "remaining_lines": "one independent prompt record per line with _record_type=prompt",
            "stream_filter": "process only records where _record_type == 'prompt'",
        },
        "prompts_content_sha256": sha256_text(
            json.dumps(prompts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        ),
        "deployment_instructions": [
            "The first JSONL line is a manifest. Skip it during inference and process only _record_type=prompt lines.",
            "Send only item.request.messages to the model. Never send ground_truth_do_not_send_to_model or source metadata.",
            "Keep prompt_id unchanged in the returned record; it is the primary join key for later analysis.",
            "Use the same selected prompt_ids for every compared model/mode. sample_pair_id supports paired method and clean/attack analysis.",
            "For a reproducible small run, filter recommended_small_scale_seed_42=true; do not resample separately on each device.",
            "Do not parse or repair model output externally. Return raw_response_text so the frozen parser can be applied centrally.",
            "If an API does not support JSON response_format or explicit reasoning controls, record the actual applied settings.",
        ],
        "inference_profiles": {
            "non_reasoning": {
                "semantic_mode": "disable hidden reasoning/thinking when the API supports it",
                "temperature": 0.0,
                "top_p": 1.0,
                "max_output_tokens": 512,
            },
            "reasoning": {
                "semantic_mode": "enable reasoning/thinking when the API supports it",
                "reasoning_effort": "high",
                "max_output_tokens_including_reasoning": 2048,
            },
        },
        "recommended_small_scale_subset": {
            "name": "portable-index-paired-100-per-label-seed-42",
            "selection": "For each dataset, sample the same 100 sorted attack-assignment indices with Python random.Random(42); use their original_ids for phishing and legitimate and include the paired clean records.",
            "indices_by_dataset": recommended_indices,
            "filter": "item.recommended_small_scale_seed_42 == true",
            "expected_main_prompts": 2400,
            "expected_ablation_prompts": 400,
            "note": "The same prompt_ids must be reused across every external model and inference mode.",
        },
        "portable_result_contract": {
            "recommended_container": "JSONL, one object per prompt/model/mode attempt",
            "required_fields": {
                "prompt_id": "string copied exactly from this export",
                "model_id": "exact deployed model/checkpoint identifier",
                "inference_mode": "non_reasoning|reasoning",
                "request_success": "boolean",
                "raw_response_text": "string|null; unmodified final answer",
                "reasoning_content": "string|null; unmodified thinking text if exposed",
                "error": "string|null",
            },
            "strongly_recommended_fields": {
                "run_id": "string identifying device/batch",
                "timestamp_utc": "ISO-8601 string",
                "latency_ms": "integer|null",
                "attempt_count": "integer",
                "response_format_applied": "boolean|null",
                "actual_request_parameters": "object",
                "usage": {
                    "input_tokens": "integer|null",
                    "reasoning_tokens": "integer|null",
                    "answer_tokens": "integer|null",
                    "api_completion_tokens": "integer|null; reasoning + answer",
                    "total_tokens": "integer|null",
                    "prompt_cache_hit_tokens": "integer|null",
                    "prompt_cache_miss_tokens": "integer|null",
                },
            },
            "example_result_record": {
                "prompt_id": "COPY_FROM_INPUT_ITEM",
                "model_id": "exact-checkpoint-name",
                "inference_mode": "non_reasoning",
                "request_success": True,
                "raw_response_text": "{\"is_phishing\":true}",
                "reasoning_content": None,
                "error": None,
                "run_id": "device-or-batch-id",
                "timestamp_utc": "2026-08-14T00:00:00Z",
                "latency_ms": None,
                "attempt_count": 1,
                "response_format_applied": True,
                "actual_request_parameters": {},
                "usage": {
                    "input_tokens": None,
                    "reasoning_tokens": None,
                    "answer_tokens": None,
                    "api_completion_tokens": None,
                    "total_tokens": None,
                    "prompt_cache_hit_tokens": None,
                    "prompt_cache_miss_tokens": None,
                },
            },
        },
        "prompt_snapshot": prompt_snapshot(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        for item in prompts:
            row = {"_record_type": "prompt", **item}
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "counts": counts,
                "file_sha256": sha256_file(args.output),
                "bytes": args.output.stat().st_size,
                "jsonl_lines": len(prompts) + 1,
                "manifest_lines": 1,
                "prompt_lines": len(prompts),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
