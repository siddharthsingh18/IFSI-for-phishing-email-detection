"""Unit tests for Ollama client, Pydantic validation, and retry handling."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from phishbench.ollama_client import (
    EmailClassificationResult,
    OllamaClient,
    OllamaConfig,
)


def test_pydantic_valid_phishing_payload() -> None:
    data = {
        "verdict": "phishing",
        "confidence": 0.95,
        "reasons": ["Urgent threat tone", "Suspicious link to unverified domain"],
    }
    result = EmailClassificationResult.model_validate(data)
    assert result.verdict == "phishing"
    assert result.confidence == 0.95
    assert len(result.reasons) == 2


def test_pydantic_valid_legitimate_payload() -> None:
    data = {
        "verdict": "legitimate",
        "confidence": 0.92,
        "reasons": ["Internal corporate correspondence between coworkers"],
    }
    result = EmailClassificationResult.model_validate(data)
    assert result.verdict == "legitimate"
    assert result.confidence == 0.92
    assert len(result.reasons) == 1


def test_pydantic_rejects_invalid_verdict() -> None:
    data = {
        "verdict": "uncertain",
        "confidence": 0.5,
        "reasons": ["Could be spam"],
    }
    with pytest.raises(ValidationError, match="Verdict must be 'phishing' or 'legitimate'"):
        EmailClassificationResult.model_validate(data)


def test_pydantic_rejects_missing_reasons() -> None:
    data = {
        "verdict": "phishing",
        "confidence": 0.9,
    }
    with pytest.raises(ValidationError):
        EmailClassificationResult.model_validate(data)


def test_pydantic_rejects_empty_reasons() -> None:
    data = {
        "verdict": "phishing",
        "confidence": 0.9,
        "reasons": [],
    }
    with pytest.raises(ValidationError):
        EmailClassificationResult.model_validate(data)


def test_pydantic_confidence_clamping_and_normalization() -> None:
    # Handle percentage confidence e.g. 95 -> 0.95
    data = {
        "verdict": "phishing",
        "confidence": 95,
        "reasons": ["Phishing indicators detected"],
    }
    res = EmailClassificationResult.model_validate(data)
    assert res.confidence == 0.95


def test_ollama_client_success_on_first_try() -> None:
    config = OllamaConfig(model="mock-model", temperature=0.0, max_retries=1)
    client = OllamaClient(config)

    valid_response_json = {
        "message": {
            "content": json.dumps({
                "verdict": "legitimate",
                "confidence": 0.89,
                "reasons": ["Standard meeting request"],
            })
        }
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = valid_response_json

    with patch.object(client.client, "post", return_value=mock_resp) as mock_post:
        res, meta = client.classify_email("Subject: Team sync tomorrow at 10")
        assert res is not None
        assert res.verdict == "legitimate"
        assert meta["is_valid"] is True
        assert meta["retries"] == 0
        assert mock_post.call_count == 1


def test_ollama_client_succeeds_on_retry() -> None:
    config = OllamaConfig(model="mock-model", temperature=0.0, max_retries=1)
    client = OllamaClient(config)

    invalid_resp = MagicMock()
    invalid_resp.status_code = 200
    invalid_resp.json.return_value = {"message": {"content": "Not valid JSON"}}

    valid_resp = MagicMock()
    valid_resp.status_code = 200
    valid_resp.json.return_value = {
        "message": {
            "content": json.dumps({
                "verdict": "phishing",
                "confidence": 0.98,
                "reasons": ["Credential harvesting form"],
            })
        }
    }

    with patch.object(client.client, "post", side_effect=[invalid_resp, valid_resp]) as mock_post:
        res, meta = client.classify_email("Subject: Your account is suspended")
        assert res is not None
        assert res.verdict == "phishing"
        assert meta["is_valid"] is True
        assert meta["retries"] == 1
        assert mock_post.call_count == 2


def test_ollama_client_invalid_equals_error_after_max_retries() -> None:
    config = OllamaConfig(model="mock-model", temperature=0.0, max_retries=1)
    client = OllamaClient(config)

    bad_resp = MagicMock()
    bad_resp.status_code = 500
    bad_resp.text = "Internal Server Error"

    with patch.object(client.client, "post", return_value=bad_resp) as mock_post:
        res, meta = client.classify_email("Subject: Test email")
        assert res is None
        assert meta["is_valid"] is False
        assert meta["retries"] == 1  # 1 initial + 1 retry = 1 retry attempted
        assert "HTTP 500" in meta["error"]
        assert mock_post.call_count == 2


def test_same_config_produces_same_prompt_hash() -> None:
    """Test that identical configs produce identical prompt template hashes."""
    cfg1 = OllamaConfig(model="qwen2.5:0.5b", temperature=0.0)
    cfg2 = OllamaConfig(model="qwen2.5:0.5b", temperature=0.0)
    assert cfg1.compute_prompt_hash() == cfg2.compute_prompt_hash()
    assert cfg1.prompt_hash == cfg2.prompt_hash

    # Same custom template produces same hash
    template = "Classify email: {{text}}"
    cfg3 = OllamaConfig(prompt_template=template)
    cfg4 = OllamaConfig(prompt_template=template)
    assert cfg3.prompt_hash == cfg4.prompt_hash
    assert cfg1.prompt_hash != cfg3.prompt_hash

