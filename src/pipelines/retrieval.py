"""
Retrieval Pipeline for RAG Query Processing

Processes queries through:
1. Query embedding generation
2. Vector similarity search in Qdrant
3. LLM-based answer generation (streaming or complete)
"""

from typing import List, Dict, Any, Iterator
from haystack.core.pipeline import Pipeline
from haystack.dataclasses import Document
from haystack.components.embedders import OpenAITextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from src.document_stores.store import QdrantDocumentStore
from src.config.settings import settings
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import openai

logger = logging.getLogger(__name__)


class ExternalServiceError(Exception):
    """Raised when external service (OpenAI, Qdrant) fails."""
    pass


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


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError)),
    reraise=True
)
def _generate_embedding_with_retry(text_embedder: OpenAITextEmbedder, query: str):
    """Generate embedding with automatic retry on transient failures."""
    return text_embedder.run(text=query)


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def _search_documents_with_retry(document_store: QdrantDocumentStore, query_embedding, top_k: int, score_threshold: float):
    """Search documents with automatic retry on transient failures."""
    return document_store.search(
        query_embedding=query_embedding,
        top_k=top_k,
        score_threshold=score_threshold
    )


def retrieve_documents(query: str, top_k: int = None) -> Dict[str, Any]:
    """
    Retrieve relevant documents and generate an answer for a query.
    
    Includes automatic retry logic and performance timing.
    
    Args:
        query: The user's question
        top_k: Number of documents to retrieve (uses settings default if not provided)
        
    Returns:
        dict: Contains retrieved documents and generated answer with timing metadata
        
    Raises:
        ExternalServiceError: If external services fail after retries
    """
    if top_k is None:
        top_k = settings.retrieval_top_k
    
    timing = {}
    overall_start = time.time()
    
    # Step 1: Create query embedding with retry
    logger.info(f"Starting retrieval for query: {query[:100]}")
    embed_start = time.time()
    
    try:
        text_embedder = get_text_embedder()
        embedding_result = _generate_embedding_with_retry(text_embedder, query)
        query_embedding = embedding_result["embedding"]
        timing["embedding_ms"] = round((time.time() - embed_start) * 1000, 2)
        logger.info(f"Embedding generated in {timing['embedding_ms']}ms")
    except Exception as e:
        logger.error(f"Embedding generation failed after retries: {e}")
        raise ExternalServiceError(f"Failed to generate embedding: {e}")
    
    # Step 2: Search Qdrant for relevant documents with retry
    search_start = time.time()
    
    try:
        document_store = get_document_store()
        documents = _search_documents_with_retry(
            document_store,
            query_embedding,
            top_k,
            settings.min_similarity_score
        )
        timing["search_ms"] = round((time.time() - search_start) * 1000, 2)
        logger.info(f"Retrieved {len(documents)} documents in {timing['search_ms']}ms")
    except Exception as e:
        logger.error(f"Document search failed after retries: {e}")
        raise ExternalServiceError(f"Failed to search documents: {e}")
    
    # Step 3: Generate answer with LLM
    gen_start = time.time()
    
    try:
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
        
        timing["generation_ms"] = round((time.time() - gen_start) * 1000, 2)
        timing["total_ms"] = round((time.time() - overall_start) * 1000, 2)
        
        logger.info(f"Answer generated in {timing['generation_ms']}ms (total: {timing['total_ms']}ms)")
        
        return {
            "query": query,
            "documents": documents,
            "answer": result["llm"]["replies"][0] if result.get("llm", {}).get("replies") else "No answer generated",
            "metadata": {
                "num_documents_retrieved": len(documents),
                "top_k": top_k,
                **timing
            }
        }
    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        raise ExternalServiceError(f"Failed to generate answer: {e}")


def retrieve_documents_streaming(query: str, top_k: int = None) -> Iterator[Dict[str, Any]]:
    """
    Retrieve documents and stream the LLM's answer token by token.
    
    Uses native OpenAI SDK for streaming support with retry logic and timing.
    
    Args:
        query: The user's question
        top_k: Number of documents to retrieve
        
    Yields:
        dict: Documents first, then individual answer tokens with timing
        
    Raises:
        ExternalServiceError: If external services fail
    """
    if top_k is None:
        top_k = settings.retrieval_top_k
    
    timing = {}
    overall_start = time.time()
    
    # Step 1: Embed the query with retry
    logger.info(f"Starting streaming retrieval for query: {query[:100]}")
    embed_start = time.time()
    
    try:
        text_embedder = get_text_embedder()
        embedding_result = _generate_embedding_with_retry(text_embedder, query)
        query_embedding = embedding_result["embedding"]
        timing["embedding_ms"] = round((time.time() - embed_start) * 1000, 2)
        logger.info(f"Embedding generated in {timing['embedding_ms']}ms")
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        yield {
            "type": "error",
            "error": f"Failed to generate embedding: {str(e)}"
        }
        return
    
    # Step 2: Search for documents with retry
    search_start = time.time()
    
    try:
        document_store = get_document_store()
        documents = _search_documents_with_retry(
            document_store,
            query_embedding,
            top_k,
            settings.min_similarity_score
        )
        timing["search_ms"] = round((time.time() - search_start) * 1000, 2)
        logger.info(f"Retrieved {len(documents)} documents in {timing['search_ms']}ms")
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        yield {
            "type": "error",
            "error": f"Failed to search documents: {str(e)}"
        }
        return
    
    # Yield documents first
    yield {
        "type": "documents",
        "data": documents,
        "metadata": {
            "num_documents_retrieved": len(documents),
            "top_k": top_k,
            **timing
        }
    }
    
    # Step 3: Stream answer from OpenAI with timeout
    gen_start = time.time()
    
    try:
        # Format documents into context string
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.content}" 
            for i, doc in enumerate(documents)
        ])
        
        # Build the prompt
        prompt = RAG_PROMPT_TEMPLATE.replace("{% for doc in documents %}\n{{ doc.content }}\n{% endfor %}", context)
        prompt = prompt.replace("{{ question }}", query)
        
        # Stream using native OpenAI SDK
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        model = settings.fallback_llm_provider.split(":")[1] if ":" in settings.fallback_llm_provider else "gpt-4o-mini"
        
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            stream=True,
            timeout=60  # 60 second timeout
        )
        
        token_count = 0
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                token_count += 1
                yield {
                    "type": "token",
                    "data": chunk.choices[0].delta.content
                }
        
        timing["generation_ms"] = round((time.time() - gen_start) * 1000, 2)
        timing["total_ms"] = round((time.time() - overall_start) * 1000, 2)
        
        logger.info(f"Streamed {token_count} tokens in {timing['generation_ms']}ms (total: {timing['total_ms']}ms)")
        
        # Send completion metadata
        yield {
            "type": "done",
            "metadata": {
                "tokens_streamed": token_count,
                **timing
            }
        }
    except openai.Timeout as e:
        logger.error(f"OpenAI request timed out after 60s: {e}")
        yield {
            "type": "error",
            "error": f"LLM generation timed out: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Streaming generation failed: {e}")
        yield {
            "type": "error",
            "error": f"Failed to stream answer: {str(e)}"
        }
