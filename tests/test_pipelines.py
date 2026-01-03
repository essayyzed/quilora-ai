import pytest
from haystack.dataclasses import Document
from src.pipelines.indexing import index_documents
from src.pipelines.retrieval import retrieve_documents

def test_index_documents():
    documents = [
        Document(content="Test document 1", embedding=[0.1] * 1536),
        Document(content="Test document 2", embedding=[0.2] * 1536)
    ]
    index_response = index_documents(documents)
    assert index_response is not None
    # Response is a dict with pipeline results
    assert isinstance(index_response, dict)

def test_retrieve_documents():
    query = "Test document"
    results = retrieve_documents(query)
    assert results is not None
    assert isinstance(results, dict)  # retrieve_documents returns a dict
    assert "answer" in results
    assert "documents" in results
    assert "metadata" in results