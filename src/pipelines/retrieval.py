"""
Retrieval Pipeline for RAG Query Processing

Processes queries through:
1. Query embedding generation
2. Vector similarity search in Qdrant
3. LLM-based answer generation
"""

from typing import List, Dict, Any
from haystack.core.pipeline import Pipeline
from haystack.dataclasses import Document
from haystack.components.embedders import OpenAITextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from src.document_stores.store import QdrantDocumentStore
from src.config.settings import settings


# RAG prompt template
RAG_PROMPT_TEMPLATE = """You are a helpful AI assistant. Answer the question based on the provided context.

Context:
{% for doc in documents %}
{{ doc.content }}
{% endfor %}

Question: {{ question }}

Provide a clear, accurate answer based solely on the context above. If the context doesn't contain enough information, say so.

Answer:"""


# Module-level cached instances (lazy-initialized)
# Avoids expensive object recreation (especially Qdrant connections) on every query
_cached_embedder = None
_cached_document_store = None


def get_text_embedder() -> OpenAITextEmbedder:
    """
    Get or create cached OpenAI text embedder.
    
    Returns:
        OpenAITextEmbedder: Singleton embedder instance
    """
    global _cached_embedder
    if _cached_embedder is None:
        _cached_embedder = OpenAITextEmbedder(
            api_key=Secret.from_token(settings.openai_api_key),
            model=settings.embedding_model
        )
    return _cached_embedder


def get_document_store() -> QdrantDocumentStore:
    """
    Get or create cached Qdrant document store.
    
    Reuses connection to avoid expensive reconnection overhead.
    
    Returns:
        QdrantDocumentStore: Singleton document store instance
    """
    global _cached_document_store
    if _cached_document_store is None:
        _cached_document_store = QdrantDocumentStore(
            collection_name=settings.qdrant_collection_name,
            embedding_dimension=settings.embedding_dimension
        )
    return _cached_document_store


def _reset_cache():
    """
    Reset cached instances.
    
    Useful for testing or when configuration changes.
    """
    global _cached_embedder, _cached_document_store
    _cached_embedder = None
    _cached_document_store = None


def retrieve_documents(query: str, top_k: int = None) -> Dict[str, Any]:
    """
    Retrieve relevant documents and generate an answer for a query.
    
    Args:
        query: The user's question
        top_k: Number of documents to retrieve (uses settings default if not provided)
        
    Returns:
        dict: Contains retrieved documents and generated answer
    """
    if top_k is None:
        top_k = settings.retrieval_top_k
    
    # Step 1: Create query embedding using cached embedder
    text_embedder = get_text_embedder()
    embedding_result = text_embedder.run(text=query)
    query_embedding = embedding_result["embedding"]
    
    # Step 2: Search Qdrant for relevant documents using cached document store
    document_store = get_document_store()
    documents = document_store.search(
        query_embedding=query_embedding,
        top_k=top_k,
        score_threshold=settings.min_similarity_score
    )
    
    # Step 3: Generate answer with LLM using a pipeline
    prompt_builder = PromptBuilder(template=RAG_PROMPT_TEMPLATE)
    llm = OpenAIGenerator(
        api_key=Secret.from_token(settings.openai_api_key),
        model=settings.fallback_llm_provider.split(":")[1] if ":" in settings.fallback_llm_provider else "gpt-4o-mini",
        generation_kwargs={
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens
        }
    )
    
    # Create a simple RAG pipeline
    rag_pipeline = Pipeline()
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("prompt_builder", "llm")
    
    # Run the pipeline with documents and question
    result = rag_pipeline.run({
        "prompt_builder": {
            "documents": documents,
            "question": query
        }
    })
    
    return {
        "query": query,
        "documents": documents,
        "answer": result["llm"]["replies"][0] if result.get("llm", {}).get("replies") else "No answer generated",
        "metadata": {
            "num_documents_retrieved": len(documents),
            "top_k": top_k
        }
    }