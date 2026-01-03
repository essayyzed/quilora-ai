"""
Integration Tests for API Endpoints

These tests require:
1. Qdrant running locally on port 6333: docker run -p 6333:6333 qdrant/qdrant
2. Valid API keys in .env file (OPENAI_API_KEY, GROQ_API_KEY)
3. Test documents indexed in Qdrant

Run with: uv run pytest tests/test_api.py -v
Skip if no setup: uv run pytest tests/test_api.py -v -m "not integration"
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.config.settings import settings

client = TestClient(app)

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def check_prerequisites():
    """Check if required services and configuration are available."""
    issues = []
    
    # Check API keys
    if not settings.openai_api_key:
        issues.append("OPENAI_API_KEY not set in .env")
    if not settings.groq_api_key:
        issues.append("GROQ_API_KEY not set in .env")
    
    # Check Qdrant connection
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        client.get_collections()
    except Exception as e:
        issues.append(f"Qdrant not accessible: {e}")
    
    if issues:
        pytest.skip(f"Prerequisites not met: {'; '.join(issues)}")


def test_query_endpoint(check_prerequisites):
    """Test successful query with valid input."""
    response = client.post("/query", json={"query": "What is RAG?"})
    
    # If Qdrant has no documents, we'll get an answer but with empty documents
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    
    data = response.json()
    assert "answer" in data, "Response should contain 'answer' field"
    assert "documents" in data, "Response should contain 'documents' field"
    assert "metadata" in data, "Response should contain 'metadata' field"
    assert isinstance(data["documents"], list), "Documents should be a list"


def test_invalid_query_endpoint(check_prerequisites):
    """Test error handling with empty query."""
    response = client.post("/query", json={"query": ""})
    assert response.status_code == 400, f"Expected 400 for empty query, got {response.status_code}"
    assert "detail" in response.json(), "Error response should contain 'detail' field"


def test_query_with_top_k(check_prerequisites):
    """Test query with custom top_k parameter."""
    response = client.post("/query", json={"query": "What is RAG?", "top_k": 3})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    # Check that top_k is respected (if documents exist)
    if data["documents"]:
        assert len(data["documents"]) <= 3, "Should return at most 3 documents"


def test_query_response_structure(check_prerequisites):
    """Test that response has correct structure."""
    response = client.post("/query", json={"query": "Test query"})
    assert response.status_code == 200
    
    data = response.json()
    # Validate response structure
    assert isinstance(data["answer"], str), "Answer should be a string"
    assert isinstance(data["documents"], list), "Documents should be a list"
    assert isinstance(data["metadata"], dict), "Metadata should be a dict"
    
    # If documents exist, validate their structure
    if data["documents"]:
        doc = data["documents"][0]
        assert "content" in doc, "Document should have 'content' field"
        assert "score" in doc, "Document should have 'score' field"
        assert isinstance(doc["score"], (int, float)), "Score should be numeric"