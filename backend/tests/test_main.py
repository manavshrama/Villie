import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint():
    response = client.post("/chat", json={"user_message": "Hello"})
    assert response.status_code == 200
    assert "bot_response" in response.json()

def test_train_endpoint():
    response = client.post("/train")
    assert response.status_code == 200
    assert "message" in response.json()
