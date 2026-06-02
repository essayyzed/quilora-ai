from fastapi import APIRouter
from src.config.settings import settings

router = APIRouter()


@router.get("/config")
async def get_config():
    return {
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "retrieval_top_k": settings.retrieval_top_k,
        "min_similarity_score": settings.min_similarity_score,
        "llm_temperature": settings.llm_temperature,
        "llm_max_tokens": settings.llm_max_tokens,
        "llm_provider_strategy": settings.llm_provider_strategy,
        "primary_llm_provider": settings.primary_llm_provider,
        "fallback_llm_provider": settings.fallback_llm_provider,
        "premium_llm_provider": settings.premium_llm_provider,
        "embedding_model": settings.embedding_model,
        "max_file_size_mb": settings.max_file_size_mb,
    }
