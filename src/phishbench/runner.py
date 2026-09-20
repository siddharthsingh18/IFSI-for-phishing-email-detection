"""Resume-safe runner for the Direct, Robust, Ours, and ablation prompts."""

from __future__ import annotations

import argparse
import json
import os
import random
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .io import read_jsonl, sha256_file, stable_id, write_json
from .prompts import METHODS, PROMPT_VERSION, build_prompt, prompt_snapshot

DEFAULT_BASE_URL = "https://api.deepseek.com"
PARSER_VERSION = "strict-json-v3-ours-no-summary-null-normalization"
_write_lock = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_output(text: str, method: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc.msg}"
    if not isinstance(value, dict):
        return None, "output_not_object"
    expected = {"is_phishing"}
    if method == "ours":
        expected = {"has_prompt_injection", "prompt_injection_summary", "is_phishing"}
    elif method == "ours_no_summary":
        expected = {"has_prompt_injection", "is_phishing"}
    if set(value) != expected:
        return None, f"wrong_keys:expected={sorted(expected)},actual={sorted(value)}"
    if type(value["is_phishing"]) is not bool:  # bool is intentionally exact
        return None, "is_phishing_not_boolean"
    # The ours_no_summary template has a legacy instruction saying "otherwise
    # use null", despite declaring has_prompt_injection as boolean.  Interpret
    # that one deterministic mismatch as false for parsing and metrics only.
    # The caller's raw response text is never modified.
    if method == "ours_no_summary" and value["has_prompt_injection"] is None:
        value = dict(value)
        value["has_prompt_injection"] = False
    if "has_prompt_injection" in value and type(value["has_prompt_injection"]) is not bool:
        return None, "has_prompt_injection_not_boolean"
    if method == "ours":
        summary = value["prompt_injection_summary"]
        if value["has_prompt_injection"]:
            if not isinstance(summary, str) or not summary.strip():
                return None, "summary_missing_when_injection_true"
        elif summary is not None:
            return None, "summary_must_be_null_when_injection_false"
    return value, None


def api_call(url: str, api_key: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def usage_fields(response: dict[str, Any]) -> dict[str, Any]:
    usage = response.get("usage") or {}
    api_completion = usage.get("completion_tokens")
    if api_completion is None:
        api_completion = usage.get("output_tokens")
    details = usage.get("completion_tokens_details") or {}
    reasoning = details.get("reasoning_tokens")
    if reasoning is None:
        reasoning = usage.get("reasoning_tokens")
    reasoning = int(reasoning or 0)
    answer = None if api_completion is None else max(0, int(api_completion) - reasoning)
    input_tokens = usage.get("prompt_tokens")
    if input_tokens is None:
        input_tokens = usage.get("input_tokens")
    return {
        "input_tokens": input_tokens,
        "reasoning_tokens": reasoning,
        "answer_tokens": answer,
        "api_completion_tokens": api_completion,
        # Backward-compatible aliases; prefer the explicit fields above.
        "completion_tokens": answer,
        "generated_tokens_including_reasoning": api_completion,
        "total_tokens": usage.get("total_tokens"),
        "prompt_cache_hit_tokens": usage.get("prompt_cache_hit_tokens"),
        "prompt_cache_miss_tokens": usage.get("prompt_cache_miss_tokens"),
    }


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _write_lock, path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {str(row["run_item_id"]) for row in read_jsonl(path) if row.get("request_success") is True}


def run_one(record: dict[str, Any], args: argparse.Namespace, api_key: str) -> dict[str, Any]:
    prompt = build_prompt(record, args.method)
    run_item_id = stable_id(record.get("email_id"), args.model, args.thinking, args.reasoning_effort, args.method, args.condition, prompt.expanded_prompt_sha256)
    payload: dict[str, Any] = {
        "model": args.model,
        "messages": prompt.messages,
        "thinking": {"type": "enabled" if args.thinking == "on" else "disabled"},
        "response_format": {"type": "json_object"},
        "max_tokens": args.max_tokens,
    }
    if args.thinking == "on":
        payload["reasoning_effort"] = args.reasoning_effort
    else:
        payload["temperature"] = args.temperature
        payload["top_p"] = args.top_p
    if args.api_seed is not None:
        payload["seed"] = args.api_seed

    started = time.perf_counter()
    response: dict[str, Any] | None = None
    error: str | None = None
    attempts = 0
    for attempts in range(1, args.retries + 2):
        try:
            response = api_call(args.base_url, api_key, payload, args.timeout)
            error = None
            break
        except Exception as exc:  # keep every exhausted failure in the denominator
            error = f"{type(exc).__name__}: {exc}"
            if attempts <= args.retries:
                time.sleep(min(8.0, 0.5 * (2 ** (attempts - 1))) + random.random() * 0.2)
    latency_ms = round((time.perf_counter() - started) * 1000)
    choice = ((response or {}).get("choices") or [{}])[0]
    message = choice.get("message") or {}
    raw_text = str(message.get("content") or "")
    parsed, parse_error = parse_output(raw_text, args.method) if response else (None, "no_response")
    return {
        "run_item_id": run_item_id,
        "timestamp_utc": utc_now(),
        "dataset": args.dataset,
        "split": "test",
        "condition": args.condition,
        "method": args.method,
        "prompt_version": PROMPT_VERSION,
        "parser_version": PARSER_VERSION,
        "prompt_sha256": prompt.expanded_prompt_sha256,
        "prompt_block_hashes": prompt.block_hashes,
        "input_file_sha256": args.input_sha256,
        "email_id": record.get("email_id"),
        "original_id": record.get("original_id") or record.get("email_id"),
        "label": record.get("label"),
        "model_requested": args.model,
        "model_returned": (response or {}).get("model"),
        "system_fingerprint": (response or {}).get("system_fingerprint"),
        "thinking": args.thinking,
        "reasoning_effort": args.reasoning_effort if args.thinking == "on" else None,
        "request_success": response is not None,
        "parse_success": parsed is not None,
        "parse_error": parse_error,
        "prediction": None if parsed is None else int(parsed["is_phishing"]),
        "has_prompt_injection": None if parsed is None else parsed.get("has_prompt_injection"),
        "prompt_injection_summary": None if parsed is None else parsed.get("prompt_injection_summary"),
        "raw_response_text": raw_text,
        "reasoning_content": message.get("reasoning_content"),
        "finish_reason": choice.get("finish_reason"),
        "usage": usage_fields(response or {}),
        "latency_ms": latency_ms,
        "attempt_count": attempts,
        "error": error,
        "raw_api_response": response,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--condition", choices=("clean", "attacked_phishing", "injected_legitimate_control"), required=True)
    parser.add_argument("--method", choices=METHODS, required=True)
    parser.add_argument("--model", choices=("deepseek-v4-flash", "deepseek-v4-pro"), required=True)
    parser.add_argument("--thinking", choices=("on", "off"), required=True)
    parser.add_argument("--reasoning-effort", choices=("high", "max"), default="high")
    parser.add_argument("--base-url", default=os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--api-key-env", default="DEEPSEEK_API_KEY")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--api-seed", type=int, help="Only set after confirming endpoint support; omitted by default.")
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.concurrency < 1:
        parser.error("--concurrency must be >= 1")
    args.input_sha256 = sha256_file(args.input)
    records = read_jsonl(args.input)
    if args.limit is not None:
        records = records[: args.limit]

    snapshot = prompt_snapshot()
    manifest = {
        "created_at_utc": utc_now(),
        "input": str(args.input),
        "input_sha256": args.input_sha256,
        "input_records_selected": len(records),
        "output": str(args.output),
        "dataset": args.dataset,
        "condition": args.condition,
        "method": args.method,
        "model": args.model,
        "thinking": args.thinking,
        "reasoning_effort": args.reasoning_effort if args.thinking == "on" else None,
        "request_parameters": {"temperature": args.temperature if args.thinking == "off" else None, "top_p": args.top_p if args.thinking == "off" else None, "api_seed": args.api_seed, "max_tokens": args.max_tokens, "response_format": {"type": "json_object"}, "retries": args.retries, "timeout": args.timeout},
        "token_accounting": {
            "input_tokens": "API prompt_tokens",
            "reasoning_tokens": "API completion_tokens_details.reasoning_tokens",
            "answer_tokens": "api_completion_tokens - reasoning_tokens",
            "api_completion_tokens": "API completion_tokens; includes reasoning and final answer",
            "total_tokens": "API total_tokens",
        },
        "prompt_snapshot": snapshot,
        "dry_run": args.dry_run,
    }
    write_json(args.manifest, manifest)
    if args.dry_run:
        preview = build_prompt(records[0], args.method) if records else None
        print(json.dumps({"manifest": str(args.manifest), "records": len(records), "first_prompt_sha256": preview.expanded_prompt_sha256 if preview else None}, indent=2))
        return

    api_key = os.getenv(args.api_key_env)
    if not api_key:
        parser.error(f"environment variable {args.api_key_env} is required unless --dry-run is used")
    done = completed_ids(args.output) if args.resume else set()
    pending = []
    for record in records:
        prompt = build_prompt(record, args.method)
        item_id = stable_id(record.get("email_id"), args.model, args.thinking, args.reasoning_effort, args.method, args.condition, prompt.expanded_prompt_sha256)
        if item_id not in done:
            pending.append(record)
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(run_one, record, args, api_key) for record in pending]
        for index, future in enumerate(as_completed(futures), 1):
            row = future.result()
            append_jsonl(args.output, row)
            status = "ok" if row["parse_success"] else "failed"
            print(f"[{index}/{len(futures)}] {row['email_id']} {status}", flush=True)


if __name__ == "__main__":
    main()
