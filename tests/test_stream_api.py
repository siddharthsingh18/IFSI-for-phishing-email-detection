from fastapi.testclient import TestClient

from api.main import app


def test_stream_endpoint_emits_typed_lane_events() -> None:
    response = TestClient(app).post(
        "/api/analyze/stream",
        json={"text": "Synthetic email body", "model": "qwen2.5:0.5b"},
    )
    assert response.status_code == 200
    assert "event: lane_started" in response.text
    assert "event: stage" in response.text
    assert "event: lane_finished" in response.text
