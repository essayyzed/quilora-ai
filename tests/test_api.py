from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_query_endpoint():
    response = client.post("/query", json={"query": "What is RAG?"})
    assert response.status_code == 200
    assert "answers" in response.json()

def test_invalid_query_endpoint():
    response = client.post("/query", json={"query": ""})
    assert response.status_code == 400
    assert "detail" in response.json()