import pytest
from fastapi.testclient import TestClient
from main import app
from app.config import get_config_value

client = TestClient(app)

API_TOKEN = get_config_value("openrouter.api_token", "your-secret-token-here-change-me")


def test_openrouter_chat_completions_real():
    response = client.post(
        "/openrouter/chat/completions",
        headers={"X-API-Token": API_TOKEN},
        json={
            "model": "x-ai/grok-code-fast-1",
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello in one word"
                }
            ]
        }
    )
    
    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    assert "id" in data
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert "message" in data["choices"][0]
    assert "content" in data["choices"][0]["message"]
    assert len(data["choices"][0]["message"]["content"]) > 0


def test_openrouter_models_list_real():
    response = client.get(
        "/openrouter/models",
        headers={"X-API-Token": API_TOKEN}
    )
    
    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    
    first_model = data["data"][0]
    assert "id" in first_model
    assert "name" in first_model or "object" in first_model


def test_openrouter_chat_completions_missing_token():
    response = client.post(
        "/openrouter/chat/completions",
        json={
            "model": "x-ai/grok-code-fast-1",
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello"
                }
            ]
        }
    )
    
    assert response.status_code == 422


def test_openrouter_models_missing_token():
    response = client.get("/openrouter/models")
    
    assert response.status_code == 422


def test_openrouter_chat_completions_invalid_token():
    response = client.post(
        "/openrouter/chat/completions",
        headers={"X-API-Token": "invalid-token"},
        json={
            "model": "x-ai/grok-code-fast-1",
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello"
                }
            ]
        }
    )
    
    assert response.status_code == 403
    assert "Invalid API token" in response.json()["detail"]


def test_openrouter_models_invalid_token():
    response = client.get(
        "/openrouter/models",
        headers={"X-API-Token": "invalid-token"}
    )
    
    assert response.status_code == 403
    assert "Invalid API token" in response.json()["detail"]

