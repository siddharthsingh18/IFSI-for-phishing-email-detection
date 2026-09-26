"""Ollama client for email classification with Pydantic validation, temperature 0, and retry handling."""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class EmailClassificationResult(BaseModel):
    """Structured classification output validated by Pydantic."""

    verdict: Literal["phishing", "legitimate"] = Field(
        ...,
        description="Final email security verdict: 'phishing' or 'legitimate'",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence score between 0.0 and 1.0",
    )
    reasons: list[str] = Field(
        ...,
        min_length=1,
        description="Explanatory indicators or rationale supporting the verdict",
    )

    @field_validator("verdict", mode="before")
    @classmethod
    def normalize_verdict(cls, value: Any) -> str:
        if isinstance(value, str):
            v = value.strip().lower()
            if v in ("phishing", "phish", "spam", "malicious", "1"):
                return "phishing"
            if v in ("legitimate", "ham", "benign", "safe", "valid", "0"):
                return "legitimate"
        raise ValueError(f"Verdict must be 'phishing' or 'legitimate', got: {value!r}")

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp_confidence(cls, value: Any) -> float:
        try:
            val = float(value)
        except (TypeError, ValueError) as err:
            raise ValueError(f"Confidence must be a numeric float: {value!r}") from err
        if val > 1.0 and val <= 100.0:
            val = val / 100.0
        return max(0.0, min(1.0, val))

    @field_validator("reasons", mode="before")
    @classmethod
    def normalize_reasons(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [value.strip()]
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            if cleaned:
                return cleaned
        raise ValueError(f"Reasons must contain at least one descriptive string, got: {value!r}")


SYSTEM_PROMPT = """You are a cybersecurity email classification system.
Your task is to analyze the email and decide if it is 'phishing' or 'legitimate'.

Rules:
1. Return ONLY a single valid JSON object.
2. The JSON object must strictly match this schema:
{
  "verdict": "phishing" or "legitimate",
  "confidence": <float between 0.0 and 1.0>,
  "reasons": ["<reason 1>", "<reason 2>", ...]
}
3. Do not include markdown codeblocks, explanation, or commentary outside the JSON object.
"""


class OllamaConfig(BaseModel):
    """Configuration for Ollama inference."""

    model: str = "qwen2.5:0.5b"
    temperature: float = 0.0
    api_base: str = "http://localhost:11434"
    timeout_seconds: float = 60.0
    max_retries: int = 1
    num_predict: int = 150
    prompt_template: str | None = None

    @classmethod
    def from_file(cls, path: Path | str) -> OllamaConfig:
        config_path = Path(path)
        if not config_path.exists():
            return cls()
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def get_prompt_template(self) -> str:
        """Return the active prompt template string for this config."""
        if self.prompt_template is not None:
            return self.prompt_template
        return SYSTEM_PROMPT

    def compute_prompt_hash(self) -> str:
        """Return sha256 hash of the prompt template determined by this config."""
        from .io import sha256_text
        return sha256_text(self.get_prompt_template())

    @property
    def prompt_hash(self) -> str:
        """Convenience property for the prompt template hash."""
        return self.compute_prompt_hash()

    def compute_config_hash(self) -> str:
        """Return deterministic sha256 hash of configuration fields."""
        from .io import sha256_text
        data = self.model_dump() if hasattr(self, "model_dump") else self.dict()
        canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return sha256_text(canonical)


class OllamaClient:
    """Ollama client with Pydantic validation and single-retry policy."""

    def __init__(self, config: OllamaConfig | None = None) -> None:
        self.config = config or OllamaConfig()
        self.client = httpx.Client(
            base_url=self.config.api_base,
            timeout=self.config.timeout_seconds,
        )

    def is_service_ready(self) -> bool:
        """Check if Ollama server is running and reachable."""
        try:
            resp = self.client.get("/api/tags", timeout=3.0)
            return resp.status_code == 200
        except Exception:
            return False

    def list_local_models(self) -> list[str]:
        """Return list of locally downloaded models."""
        try:
            resp = self.client.get("/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def classify_email(self, email_text: str) -> tuple[EmailClassificationResult | None, dict[str, Any]]:
        """Classify an email with strict JSON output, temperature 0, and max 1 retry."""
        url = "/api/chat"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this email:\n\n{email_text}"},
        ]
        payload = {
            "model": self.config.model,
            "messages": messages,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.num_predict,
            },
        }

        retries_used = 0
        last_error: str | None = None
        raw_response_content = ""
        start_time = time.perf_counter()

        max_attempts = 1 + self.config.max_retries  # 1 initial attempt + max 1 retry

        for attempt in range(max_attempts):
            if attempt > 0:
                retries_used += 1

            try:
                response = self.client.post(url, json=payload)
                if response.status_code != 200:
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    continue

                res_json = response.json()
                message_content = res_json.get("message", {}).get("content", "").strip()
                raw_response_content = message_content

                # Parse and validate with Pydantic
                parsed_data = json.loads(message_content)
                validated = EmailClassificationResult.model_validate(parsed_data)
                latency = time.perf_counter() - start_time

                metadata = {
                    "is_valid": True,
                    "retries": retries_used,
                    "latency_seconds": round(latency, 4),
                    "raw_response": raw_response_content,
                    "error": None,
                }
                return validated, metadata

            except (json.JSONDecodeError, Exception) as exc:
                last_error = f"{type(exc).__name__}: {str(exc)}"

        latency = time.perf_counter() - start_time
        metadata = {
            "is_valid": False,
            "retries": retries_used,
            "latency_seconds": round(latency, 4),
            "raw_response": raw_response_content,
            "error": last_error or "Unknown error",
        }
        return None, metadata


def run_ollama_evaluation(
    test_jsonl: Path,
    output_predictions_path: Path,
    summary_output_path: Path | None = None,
    config_path: Path | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Run Ollama evaluation on test emails."""
    config = OllamaConfig.from_file(config_path) if config_path else OllamaConfig()
    client = OllamaClient(config)

    records: list[dict[str, Any]] = []
    with test_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line.strip()))
                if len(records) >= limit:
                    break

    output_predictions_path.parent.mkdir(parents=True, exist_ok=True)
    predictions: list[dict[str, Any]] = []
    start_total_time = time.perf_counter()

    valid_count = 0
    invalid_count = 0
    y_true: list[int] = []
    y_pred: list[int] = []

    with output_predictions_path.open("w", encoding="utf-8") as out_f:
        for idx, rec in enumerate(records, start=1):
            email_id = rec.get("id", f"email-{idx}")
            true_label = int(rec.get("label", 0))
            text = rec.get("text", "")

            result, meta = client.classify_email(text)

            is_valid = meta["is_valid"]
            if is_valid and result is not None:
                valid_count += 1
                pred_label = 1 if result.verdict == "phishing" else 0
                y_true.append(true_label)
                y_pred.append(pred_label)
                verdict_str = result.verdict
                confidence_val = result.confidence
                reasons_list = result.reasons
            else:
                invalid_count += 1
                pred_label = None
                verdict_str = "error"
                confidence_val = None
                reasons_list = []

            pred_record = {
                "id": email_id,
                "true_label": true_label,
                "true_label_name": "phishing" if true_label == 1 else "legitimate",
                "predicted_verdict": verdict_str,
                "predicted_label": pred_label,
                "confidence": confidence_val,
                "reasons": reasons_list,
                "is_valid": is_valid,
                "retries": meta["retries"],
                "latency_seconds": meta["latency_seconds"],
                "error": meta["error"],
            }
            predictions.append(pred_record)
            out_f.write(json.dumps(pred_record, ensure_ascii=False) + "\n")

    total_runtime = time.perf_counter() - start_total_time
    total_samples = len(records)
    invalid_rate = (invalid_count / total_samples) if total_samples > 0 else 0.0

    # Calculate metrics on valid predictions
    metrics = {}
    if y_true and y_pred and len(y_true) == len(y_pred):
        from .baseline import compute_metrics

        metrics = compute_metrics(y_true, y_pred)

    summary = {
        "model": config.model,
        "temperature": config.temperature,
        "total_emails_evaluated": total_samples,
        "total_runtime_seconds": round(total_runtime, 4),
        "avg_latency_per_email_seconds": round(total_runtime / total_samples, 4) if total_samples > 0 else 0.0,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "invalid_rate": round(invalid_rate, 4),
        "metrics_on_valid": metrics,
        "predictions_file": str(output_predictions_path),
    }

    if summary_output_path:
        summary_output_path.parent.mkdir(parents=True, exist_ok=True)
        with summary_output_path.open("w", encoding="utf-8") as sum_f:
            json.dump(summary, sum_f, indent=2)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", type=Path, default=Path("data/splits/test.jsonl"), help="Path to test JSONL split")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/ollama_predictions_50.jsonl"),
        help="Path to save predictions",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/ollama_summary_50.json"),
        help="Path to save summary",
    )
    parser.add_argument("--config", type=Path, default=Path("config/ollama_config.json"), help="Config file")
    parser.add_argument("--limit", type=int, default=50, help="Number of test emails to evaluate")
    args = parser.parse_args()

    summary = run_ollama_evaluation(
        test_jsonl=args.test,
        output_predictions_path=args.output,
        summary_output_path=args.summary,
        config_path=args.config,
        limit=args.limit,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
