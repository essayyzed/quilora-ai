# Quilora Tests

This directory contains tests for the Quilora RAG application.

## Test Types

### Unit Tests
- `test_document_store.py` - Tests for Qdrant document store operations
- Fast, isolated tests that can run independently

### Integration Tests
- `test_api.py` - End-to-end API tests requiring full setup
- `test_pipelines.py` - Pipeline integration tests (if created)

## Running Tests

### All tests (requires full setup)
```bash
uv run pytest tests/ -v
```

### Unit tests only (requires only Qdrant)
```bash
uv run pytest tests/test_document_store.py -v
```

### Integration tests only
```bash
uv run pytest tests/ -v -m integration
```

### Skip integration tests
```bash
uv run pytest tests/ -v -m "not integration"
```

## Prerequisites for Integration Tests

### 1. Start Qdrant
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Set up environment variables
Create a `.env` file with:
```bash
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
# Optional
ANTHROPIC_API_KEY=your_key_here
```

### 3. (Optional) Index test documents
```python
from haystack.dataclasses import Document
from src.pipelines.indexing import index_documents

docs = [
    Document(content="RAG stands for Retrieval-Augmented Generation..."),
    Document(content="Machine learning is a subset of AI..."),
]
index_documents(docs)
```

## Test Coverage

To see test coverage:
```bash
uv run pytest tests/ --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## Writing New Tests

### Unit Test Example
```python
def test_my_function():
    result = my_function(input)
    assert result == expected
```

### Integration Test Example
```python
@pytest.mark.integration
def test_api_endpoint(check_prerequisites):
    response = client.post("/endpoint", json={"data": "test"})
    assert response.status_code == 200
```

## Troubleshooting

**Import errors**: Make sure to sync dependencies
```bash
uv sync --all-extras
```

**Qdrant connection fails**: Check if Docker container is running
```bash
docker ps | grep qdrant
```

**API key errors**: Verify `.env` file exists and has correct keys
```bash
grep -E "OPENAI_API_KEY|GROQ_API_KEY" .env
```
