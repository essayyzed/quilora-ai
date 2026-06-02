"""
Retrieval Pipeline for RAG Query Processing

Processes queries through:
1. Query embedding generation
2. Vector similarity search in Qdrant
3. LLM-based answer generation (streaming or complete) via aisuite multi-provider support
"""

from typing import List, Dict, Any, Iterator, Optional
from haystack.core.pipeline import Pipeline
from haystack.dataclasses import Document
from haystack.components.embedders import OpenAITextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from src.document_stores.store import QdrantDocumentStore
from src.config.settings import settings
from src.llm.router import get_router
from src.llm.provider import get_provider_registry
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


def retrieve_documents(
    query: str,
    top_k: int = None,
    provider_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve relevant documents and generate an answer for a query.
    
    Includes automatic retry logic, performance timing, and multi-provider support.
    
    Args:
        query: The user's question
        top_k: Number of documents to retrieve (uses settings default if not provided)
        provider_override: Optional manual provider selection (openai|anthropic|groq)
        
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
    
    # Step 3: Select provider and generate answer with multi-provider support
    gen_start = time.time()
    
    try:
        # Select provider using router
        router = get_router()
        provider_name, model = router.select_provider(query, provider_override)
        
        # Get provider registry and aisuite client
        registry = get_provider_registry()
        client = registry.client
        
        # Build prompt with documents
        context = "\n\n".join([f"Document {i+1}:\n{doc.content}" for i, doc in enumerate(documents)])
        prompt = RAG_PROMPT_TEMPLATE.replace("{% for doc in documents %}\n{{ doc.content }}\n{% endfor %}", context)
        prompt = prompt.replace("{{ question }}", query)
        
        # Generate answer using aisuite with fallback chain
        answer = None
        provider_used = provider_name
        fallback_occurred = False
        
        # Try primary provider
        try:
            messages = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model=f"{provider_name}:{model}",
                messages=messages,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
            answer = response.choices[0].message.content
            registry.record_request_success(provider_name)
            
        except Exception as primary_error:
            logger.warning(f"Primary provider {provider_name} failed: {primary_error}")
            registry.record_request_failure(provider_name, str(primary_error))
            
            # Try fallback chain
            fallback_chain = router.get_fallback_chain(provider_name)
            for fallback_provider, fallback_model in fallback_chain:
                try:
                    logger.info(f"Attempting fallback: {fallback_provider}:{fallback_model}")
                    response = client.chat.completions.create(
                        model=f"{fallback_provider}:{fallback_model}",
                        messages=messages,
                        temperature=settings.llm_temperature,
                        max_tokens=settings.llm_max_tokens,
                    )
                    answer = response.choices[0].message.content
                    provider_used = fallback_provider
                    fallback_occurred = True
                    registry.record_request_success(fallback_provider)
                    logger.info(f"Fallback successful with {fallback_provider}")
                    break
                except Exception as fallback_error:
                    logger.warning(f"Fallback provider {fallback_provider} failed: {fallback_error}")
                    registry.record_request_failure(fallback_provider, str(fallback_error))
                    continue
            
            if answer is None:
                raise ExternalServiceError(f"All LLM providers failed. Last error: {primary_error}")
        
        timing["generation_ms"] = round((time.time() - gen_start) * 1000, 2)
        timing["total_ms"] = round((time.time() - overall_start) * 1000, 2)
        
        logger.info(
            f"Answer generated by {provider_used} in {timing['generation_ms']}ms "
            f"(total: {timing['total_ms']}ms, fallback: {fallback_occurred})"
        )
        
        return {
            "query": query,
            "documents": documents,
            "answer": answer or "No answer generated",
            "metadata": {
                "num_documents_retrieved": len(documents),
                "top_k": top_k,
                "provider_used": provider_used,
                "provider_fallback": fallback_occurred,
                **timing
            }
        }
    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        raise ExternalServiceError(f"Failed to generate answer: {e}")


def retrieve_documents_streaming(
    query: str,
    top_k: int = None,
    provider_override: Optional[str] = None
) -> Iterator[Dict[str, Any]]:
    """
    Retrieve documents and stream the LLM's answer token by token.
    
    Uses aisuite with multi-provider support, retry logic, and timing.
    
    Args:
        query: The user's question
        top_k: Number of documents to retrieve
        provider_override: Optional manual provider selection (openai|anthropic|groq)
        
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
    
    # Step 3: Select provider and stream answer with multi-provider support
    gen_start = time.time()
    
    try:
        # Select provider using router
        router = get_router()
        provider_name, model = router.select_provider(query, provider_override)
        
        # Get provider registry and aisuite client
        registry = get_provider_registry()
        client = registry.client
        
        # Format documents into context string
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.content}" 
            for i, doc in enumerate(documents)
        ])
        
        # Build the prompt
        prompt = RAG_PROMPT_TEMPLATE.replace("{% for doc in documents %}\n{{ doc.content }}\n{% endfor %}", context)
        prompt = prompt.replace("{{ question }}", query)
        
        # Try primary provider with streaming
        provider_used = provider_name
        fallback_occurred = False
        stream_started = False
        
        try:
            messages = [{"role": "user", "content": prompt}]
            stream = client.chat.completions.create(
                model=f"{provider_name}:{model}",
                messages=messages,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                stream=True,
            )
            
            token_count = 0
            for chunk in stream:
                stream_started = True
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    token_count += 1
                    yield {
                        "type": "token",
                        "data": chunk.choices[0].delta.content
                    }
            
            registry.record_request_success(provider_name)
            
            timing["generation_ms"] = round((time.time() - gen_start) * 1000, 2)
            timing["total_ms"] = round((time.time() - overall_start) * 1000, 2)
            
            logger.info(
                f"Streamed {token_count} tokens from {provider_used} in {timing['generation_ms']}ms "
                f"(total: {timing['total_ms']}ms)"
            )
            
            # Send completion metadata
            yield {
                "type": "done",
                "metadata": {
                    "tokens_streamed": token_count,
                    "provider_used": provider_used,
                    "provider_fallback": fallback_occurred,
                    **timing
                }
            }
            
        except Exception as primary_error:
            logger.warning(f"Primary provider {provider_name} failed: {primary_error}")
            registry.record_request_failure(provider_name, str(primary_error))
            
            # If streaming already started, we can't fallback gracefully
            if stream_started:
                yield {
                    "type": "error",
                    "error": f"Stream interrupted from {provider_name}: {str(primary_error)}"
                }
                return
            
            # Try fallback chain (only if stream hasn't started yet)
            fallback_chain = router.get_fallback_chain(provider_name)
            fallback_success = False
            
            for fallback_provider, fallback_model in fallback_chain:
                try:
                    logger.info(f"Attempting fallback: {fallback_provider}:{fallback_model}")
                    stream = client.chat.completions.create(
                        model=f"{fallback_provider}:{fallback_model}",
                        messages=messages,
                        temperature=settings.llm_temperature,
                        max_tokens=settings.llm_max_tokens,
                        stream=True,
                    )
                    
                    token_count = 0
                    for chunk in stream:
                        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                            token_count += 1
                            yield {
                                "type": "token",
                                "data": chunk.choices[0].delta.content
                            }
                    
                    provider_used = fallback_provider
                    fallback_occurred = True
                    fallback_success = True
                    registry.record_request_success(fallback_provider)
                    
                    timing["generation_ms"] = round((time.time() - gen_start) * 1000, 2)
                    timing["total_ms"] = round((time.time() - overall_start) * 1000, 2)
                    
                    logger.info(f"Fallback successful: streamed {token_count} tokens from {fallback_provider}")
                    
                    yield {
                        "type": "done",
                        "metadata": {
                            "tokens_streamed": token_count,
                            "provider_used": provider_used,
                            "provider_fallback": fallback_occurred,
                            **timing
                        }
                    }
                    break
                    
                except Exception as fallback_error:
                    logger.warning(f"Fallback provider {fallback_provider} failed: {fallback_error}")
                    registry.record_request_failure(fallback_provider, str(fallback_error))
                    continue
            
            if not fallback_success:
                yield {
                    "type": "error",
                    "error": f"All LLM providers failed. Last error: {str(primary_error)}"
                }
                
    except Exception as e:
        logger.error(f"Streaming generation failed: {e}")
        yield {
            "type": "error",
            "error": f"Failed to stream answer: {str(e)}"
        }
