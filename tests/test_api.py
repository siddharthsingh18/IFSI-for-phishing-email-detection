"""Tests for FastAPI backend endpoints."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is on sys.path
root_dir = Path(__file__).resolve().parents[1]
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_root_endpoint() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert data["docs_url"] == "/docs"
    assert data["health_url"] == "/health"


def test_health_endpoint_schema() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()

    assert "status" in data
    assert "ollama" in data
    assert "faiss" in data
    assert "environment" in data

    assert "connected" in data["ollama"]
    assert "api_base" in data["ollama"]
    assert "available_models" in data["ollama"]
    assert "message" in data["ollama"]

    assert "loaded" in data["faiss"]
    assert "index_path" in data["faiss"]
    assert "index_size" in data["faiss"]
    assert "message" in data["faiss"]

    assert "python_version" in data["environment"]
    assert "package" in data["environment"]


def test_model_catalog_does_not_promote_missing_primary_artifact() -> None:
    data = client.get("/models").json()
    assert data["primary_model"] == "qwen2.5:0.5b"
    llama = next(item for item in data["available_models"] if item["id"] == "llama3.2:3b")
    assert llama["role"] == "candidate"


def test_cors_headers() -> None:
    resp = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"

    fallback_port_resp = client.get("/health", headers={"Origin": "http://localhost:5174"})
    assert fallback_port_resp.status_code == 200
    assert fallback_port_resp.headers.get("access-control-allow-origin") == "http://localhost:5174"


def test_docs_endpoint() -> None:
    resp = client.get("/docs")
    assert resp.status_code == 200
    assert "swagger" in resp.text.lower() or "html" in resp.text.lower()
