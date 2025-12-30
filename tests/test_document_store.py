"""
Tests for Qdrant Document Store

Run with: uv run pytest tests/test_document_store.py -v
"""

import pytest
from haystack import Document
from src.document_stores.store import QdrantDocumentStore


@pytest.fixture
def document_store():
    """Create a test document store."""
    store = QdrantDocumentStore(
        collection_name="test_documents",
        embedding_dimension=128,  # Small dimension for testing
    )
    yield store
    # Cleanup after test
    try:
        store.delete_collection()
    except:
        pass


def test_write_and_count_documents(document_store):
    """Test writing documents and counting them."""
    # Create test documents with embeddings
    docs = [
        Document(
            id="doc1",
            content="This is a test document about AI.",
            embedding=[0.1] * 128,
            meta={"source": "test"},
        ),
        Document(
            id="doc2",
            content="Another document about machine learning.",
            embedding=[0.2] * 128,
            meta={"source": "test"},
        ),
    ]
    
    # Write documents
    written = document_store.write_documents(docs)
    assert written == 2
    
    # Count documents
    count = document_store.count_documents()
    assert count == 2


def test_search_documents(document_store):
    """Test similarity search."""
    # Write test documents
    docs = [
        Document(
            id="doc1",
            content="AI and machine learning",
            embedding=[0.1] * 128,
        ),
        Document(
            id="doc2",
            content="Deep learning neural networks",
            embedding=[0.9] * 128,
        ),
    ]
    document_store.write_documents(docs)
    
    # Search with similar embedding to doc1
    query_embedding = [0.15] * 128
    results = document_store.search(query_embedding, top_k=2)
    
    assert len(results) == 2
    assert all(hasattr(doc, "score") for doc in results)
    assert all(doc.score is not None for doc in results)


def test_delete_documents(document_store):
    """Test deleting documents."""
    # Write documents
    docs = [
        Document(
            id=f"doc{i}",
            content=f"Test document {i}",
            embedding=[0.1 * i] * 128,
        )
        for i in range(1, 4)
    ]
    document_store.write_documents(docs)
    
    # Delete one document
    deleted = document_store.delete_documents(document_ids=["doc1"])
    assert deleted == 1
    
    # Verify count
    count = document_store.count_documents()
    assert count == 2


def test_write_documents_without_embeddings(document_store):
    """Test handling documents without embeddings."""
    docs = [
        Document(id="doc1", content="No embedding"),
    ]
    
    # Should skip documents without embeddings
    written = document_store.write_documents(docs)
    assert written == 0


def test_search_with_filters(document_store):
    """Test search with metadata filters."""
    docs = [
        Document(
            id="doc1",
            content="Python programming",
            embedding=[0.1] * 128,
            meta={"language": "python", "topic": "programming"},
        ),
        Document(
            id="doc2",
            content="JavaScript web dev",
            embedding=[0.2] * 128,
            meta={"language": "javascript", "topic": "webdev"},
        ),
    ]
    document_store.write_documents(docs)
    
    # Search with filter
    results = document_store.search(
        query_embedding=[0.15] * 128,
        top_k=5,
        filters={"language": "python"},
    )
    
    assert len(results) == 1
    assert results[0].meta["language"] == "python"
