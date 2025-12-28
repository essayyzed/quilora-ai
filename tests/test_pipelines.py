import pytest
from src.pipelines.indexing import index_documents
from src.pipelines.retrieval import retrieve_documents

def test_index_documents():
    documents = [{"content": "Test document 1"}, {"content": "Test document 2"}]
    index_response = index_documents(documents)
    assert index_response is not None
    assert len(index_response) == len(documents)

def test_retrieve_documents():
    query = "Test document"
    results = retrieve_documents(query)
    assert results is not None
    assert isinstance(results, list)  # Ensure results are in list format
    assert all("content" in result for result in results)  # Check if 'content' key exists in results