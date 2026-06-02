"""
Pytest Configuration and Shared Fixtures

Provides mocked LLM providers and other test utilities.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Iterator


@pytest.fixture
def mock_aisuite_client():
    """Mock aisuite client for LLM calls."""
    with patch('src.llm.provider.aisuite.Client') as mock_client_class:
        # Create mock client instance
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock chat.completions.create for non-streaming
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a mocked AI response based on the provided documents."
        mock_client.chat.completions.create.return_value = mock_response
        
        yield mock_client


@pytest.fixture
def mock_aisuite_streaming():
    """Mock aisuite client for streaming LLM calls."""
    with patch('src.llm.provider.aisuite.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock streaming response
        def mock_stream():
            tokens = ["This ", "is ", "a ", "streamed ", "response."]
            for token in tokens:
                chunk = Mock()
                chunk.choices = [Mock()]
                chunk.choices[0].delta.content = token
                yield chunk
        
        mock_client.chat.completions.create.return_value = mock_stream()
        
        yield mock_client


@pytest.fixture
def mock_provider_registry():
    """Mock LLM provider registry."""
    # Mock at the module level where it's used
    with patch('src.pipelines.retrieval.get_provider_registry') as mock_get_registry:
        
        mock_registry = Mock()
        
        # Mock client with successful response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Mocked AI response."
        mock_client.chat.completions.create.return_value = mock_response
        
        mock_registry.client = mock_client
        mock_registry.record_request_success = Mock()
        mock_registry.record_request_failure = Mock()
        mock_registry.get_all_health.return_value = {
            "openai": {"status": "healthy", "error_rate": 0.0, "last_success": "2026-01-04T00:00:00Z"},
            "anthropic": {"status": "healthy", "error_rate": 0.0, "last_success": "2026-01-04T00:00:00Z"},
            "groq": {"status": "healthy", "error_rate": 0.0, "last_success": "2026-01-04T00:00:00Z"}
        }
        
        mock_get_registry.return_value = mock_registry
        yield mock_registry


@pytest.fixture
def mock_router():
    """Mock LLM provider router."""
    # Mock at the module level where it's used
    with patch('src.pipelines.retrieval.get_router') as mock_get_router:
        mock_router_instance = Mock()
        mock_router_instance.select_provider.return_value = ("openai", "gpt-4o-mini")
        mock_router_instance.get_fallback_chain.return_value = [("anthropic", "claude-3-5-sonnet-20241022"), ("groq", "llama-3.1-70b-versatile")]
        
        mock_get_router.return_value = mock_router_instance
        yield mock_router_instance


@pytest.fixture
def mock_llm_components(mock_provider_registry, mock_router):
    """Convenience fixture that mocks all LLM components at once."""
    # Also mock the retrieval functions to avoid real LLM calls
    with patch('src.pipelines.retrieval._generate_embedding_with_retry') as mock_embed, \
         patch('src.pipelines.retrieval._search_documents_with_retry') as mock_search:
        
        # Mock embedding with retry
        mock_embed.return_value = {"embedding": [0.1] * 1536}
        
        # Mock search with sample documents
        from haystack.dataclasses import Document
        mock_search.return_value = [
            Document(content="RAG stands for Retrieval-Augmented Generation.", score=0.95),
            Document(content="It combines information retrieval with language models.", score=0.87),
            Document(content="This improves accuracy and reduces hallucinations.", score=0.82)
        ]
        
        yield {
            "registry": mock_provider_registry,
            "router": mock_router,
            "embed": mock_embed,
            "search": mock_search
        }


@pytest.fixture
def sample_documents():
    """Sample documents for testing retrieval."""
    from haystack.dataclasses import Document
    
    return [
        Document(content="RAG stands for Retrieval-Augmented Generation.", score=0.95),
        Document(content="It combines information retrieval with language models.", score=0.87),
        Document(content="This improves accuracy and reduces hallucinations.", score=0.82)
    ]


@pytest.fixture
def mock_embedder():
    """Mock text embedder."""
    with patch('src.pipelines.retrieval.get_text_embedder') as mock_get_embedder:
        mock_embedder_instance = Mock()
        mock_embedder_instance.run.return_value = {
            "embedding": [0.1] * 1536  # Mock embedding vector
        }
        mock_get_embedder.return_value = mock_embedder_instance
        yield mock_embedder_instance


@pytest.fixture
def mock_document_store(sample_documents):
    """Mock document store."""
    with patch('src.pipelines.retrieval.get_document_store') as mock_get_store:
        mock_store_instance = Mock()
        mock_store_instance.search.return_value = sample_documents
        mock_store_instance.count_documents.return_value = len(sample_documents)
        mock_store_instance.collection_name = "test_collection"
        mock_get_store.return_value = mock_store_instance
        yield mock_store_instance
