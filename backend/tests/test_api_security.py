import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import uuid
from datetime import date

from app.main import app
from app.db.session import get_db

client = TestClient(app)


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert "Konteks Indonesia" in res.json().get("project", "")


def test_today_endpoint_does_not_leak_secret():
    # Mock game service to avoid requiring running postgres during unit test
    mock_game = MagicMock()
    mock_game.id = uuid.uuid4()
    mock_game.game_date = date(2026, 10, 5)

    with patch("app.services.game_service.GameService.get_or_create_daily_game", return_value=mock_game):
        res = client.get("/api/game/today")
        assert res.status_code == 200
        data = res.json()
        assert "game_id" in data
        assert "game_date" in data
        # CRITICAL SECURITY CHECK: secret_word must not be present!
        assert "secret_word" not in data
        assert "secret_word_id" not in data


def test_sql_injection_payload_sanitized():
    payload = {
        "game_id": str(uuid.uuid4()),
        "word": "' OR '1'='1' --",
        "session_id": "test_session_sql"
    }
    res = client.post("/api/game/guess", json=payload)
    # Must fail validation cleanly (400 or 404 or 422), never 500 error
    assert res.status_code in [400, 404, 422]
    assert "secret_word" not in res.text


def test_excessively_long_word_rejected():
    payload = {
        "game_id": str(uuid.uuid4()),
        "word": "a" * 100,
        "session_id": "test_session_long"
    }
    res = client.post("/api/game/guess", json=payload)
    assert res.status_code == 422  # Pydantic max_length validation
