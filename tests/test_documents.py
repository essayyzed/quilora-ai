"""
Integration Tests for Document Management and Health Endpoints

These tests require:
1. Qdrant running locally on port 6333: docker run -p 6333:6333 qdrant/qdrant
2. Valid API keys in .env file (OPENAI_API_KEY)

Run with: uv run pytest tests/test_documents.py -v
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
    
    # Check Qdrant connection
    try:
        from qdrant_client import QdrantClient
        qdrant_client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        qdrant_client.get_collections()
    except Exception as e:
        issues.append(f"Qdrant not accessible: {e}")
    
    if issues:
        pytest.skip(f"Prerequisites not met: {'; '.join(issues)}")


# ============================================================================
# Health Endpoint Tests
# ============================================================================

class TestHealthEndpoint:
    """Tests for GET /health endpoint."""
    
    def test_health_check_success(self, check_prerequisites):
        """Test health check returns healthy status when Qdrant is available."""
        response = client.get("/health")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["qdrant"] == "connected"
        assert "timestamp" in data
        assert "document_count" in data
        assert isinstance(data["document_count"], int)
    
    def test_health_check_response_structure(self, check_prerequisites):
        """Test health check response has correct structure."""
        response = client.get("/health")
        
        data = response.json()
        required_fields = ["status", "qdrant", "timestamp"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


# ============================================================================
# Document Creation Tests
# ============================================================================

class TestDocumentCreation:
    """Tests for POST /documents endpoint."""
    
    def test_create_document_success(self, check_prerequisites):
        """Test creating a document with valid content."""
        response = client.post(
            "/documents",
            json={
                "content": "This is a test document about artificial intelligence and machine learning.",
                "metadata": {"source": "test", "author": "pytest"}
            }
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
        
        data = response.json()
        assert "document_id" in data
        assert "chunk_count" in data
        assert data["chunk_count"] >= 1
        assert "message" in data
    
    def test_create_document_empty_content(self, check_prerequisites):
        """Test error when creating document with empty content."""
        response = client.post(
            "/documents",
            json={"content": ""}
        )
        
        # Pydantic validates min_length=1, returns 422
        assert response.status_code == 422
    
    def test_create_document_whitespace_only(self, check_prerequisites):
        """Test error when creating document with only whitespace."""
        response = client.post(
            "/documents",
            json={"content": "   \n\t  "}
        )
        
        assert response.status_code == 400
    
    def test_create_document_without_metadata(self, check_prerequisites):
        """Test creating a document without metadata."""
        response = client.post(
            "/documents",
            json={"content": "Document without metadata for testing purposes."}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "document_id" in data


# ============================================================================
# File Upload Tests
# ============================================================================

class TestFileUpload:
    """Tests for POST /documents/upload endpoint."""
    
    def test_upload_txt_file(self, check_prerequisites):
        """Test uploading a .txt file."""
        content = b"This is a test file content for RAG indexing."
        
        response = client.post(
            "/documents/upload",
            files={"file": ("test.txt", content, "text/plain")}
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
        
        data = response.json()
        assert "document_id" in data
        assert "chunk_count" in data
        assert "test.txt" in data["message"]
    
    def test_upload_md_file(self, check_prerequisites):
        """Test uploading a .md file."""
        content = b"# Test Markdown\n\nThis is a test markdown file."
        
        response = client.post(
            "/documents/upload",
            files={"file": ("readme.md", content, "text/markdown")}
        )
        
        assert response.status_code == 201
    
    def test_upload_unsupported_file(self, check_prerequisites):
        """Test error when uploading unsupported file type."""
        content = b"Some content"
        
        response = client.post(
            "/documents/upload",
            files={"file": ("test.pdf", content, "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]
    
    def test_upload_empty_file(self, check_prerequisites):
        """Test error when uploading empty file."""
        response = client.post(
            "/documents/upload",
            files={"file": ("empty.txt", b"", "text/plain")}
        )
        
        assert response.status_code == 400


# ============================================================================
# Document Listing Tests
# ============================================================================

class TestDocumentListing:
    """Tests for GET /documents endpoint."""
    
    def test_list_documents(self, check_prerequisites):
        """Test listing documents."""
        response = client.get("/documents")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "documents" in data
        assert "total_count" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["documents"], list)
    
    def test_list_documents_pagination(self, check_prerequisites):
        """Test document listing with pagination."""
        response = client.get("/documents?limit=5&offset=0")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 5
        assert data["offset"] == 0
        assert len(data["documents"]) <= 5
    
    def test_list_documents_invalid_limit(self, check_prerequisites):
        """Test error with invalid limit parameter."""
        response = client.get("/documents?limit=0")
        
        assert response.status_code == 422  # Validation error
    
    def test_list_documents_max_limit(self, check_prerequisites):
        """Test error with limit exceeding max."""
        response = client.get("/documents?limit=500")
        
        assert response.status_code == 422  # Validation error


# ============================================================================
# Document Deletion Tests
# ============================================================================

class TestDocumentDeletion:
    """Tests for DELETE /documents endpoints."""
    
    def test_delete_document_by_id(self, check_prerequisites):
        """Test deleting a document by ID."""
        # First create a document
        create_response = client.post(
            "/documents",
            json={"content": "Document to be deleted."}
        )
        assert create_response.status_code == 201
        doc_id = create_response.json()["document_id"]
        
        # Then delete it
        delete_response = client.delete(f"/documents/{doc_id}")
        
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert doc_id in data["message"] or data.get("document_id") == doc_id
    
    def test_delete_all_requires_confirmation(self, check_prerequisites):
        """Test that bulk delete requires all=true parameter."""
        response = client.delete("/documents")
        
        assert response.status_code == 400
        assert "all=true" in response.json()["detail"]
    
    def test_delete_all_documents(self, check_prerequisites):
        """Test deleting all documents with confirmation."""
        # First ensure there's at least one document
        client.post("/documents", json={"content": "Temporary document."})
        
        # Delete all
        response = client.delete("/documents?all=true")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted_count" in data or "Deleted" in data["message"]


# ============================================================================
# Root Endpoint Test
# ============================================================================

class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
