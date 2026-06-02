"""
LLM Provider Registry

Manages initialization and health tracking for multiple LLM providers via aisuite.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import aisuite
from src.config.settings import settings

logger = logging.getLogger(__name__)


class ProviderHealth:
    """Track health status for a single provider."""

    def __init__(self):
        self.status: str = "unknown"
        self.error_rate: float = 0.0
        self.total_requests: int = 0
        self.failed_requests: int = 0
        self.last_success: Optional[datetime] = None
        self.last_error: Optional[str] = None

    def record_success(self):
        self.total_requests += 1
        self.last_success = datetime.utcnow()
        self.status = "healthy"
        self.error_rate = self.failed_requests / self.total_requests

    def record_failure(self, error: str):
        self.total_requests += 1
        self.failed_requests += 1
        self.last_error = error
        self.status = "unhealthy"
        self.error_rate = self.failed_requests / self.total_requests


class LLMProviderRegistry:
    """
    Registry for managing multiple LLM providers via aisuite.

    Handles initialization, health tracking, and provider access.
    """

    def __init__(self):
        provider_config = {}
        if settings.openai_api_key:
            provider_config["openai"] = {"api_key": settings.openai_api_key}
        if settings.anthropic_api_key:
            provider_config["anthropic"] = {"api_key": settings.anthropic_api_key}
        if settings.groq_api_key:
            provider_config["groq"] = {"api_key": settings.groq_api_key}

        self.client = aisuite.Client(provider_config)

        self.provider_health: Dict[str, ProviderHealth] = {
            "openai": ProviderHealth(),
            "anthropic": ProviderHealth(),
            "groq": ProviderHealth(),
        }

        logger.info(f"LLM provider registry initialized with {len(provider_config)} configured providers")

    def get_available_providers(self) -> List[str]:
        return [name for name, h in self.provider_health.items() if h.status in ("healthy", "unknown")]

    def is_provider_available(self, provider_name: str) -> bool:
        health = self.provider_health.get(provider_name)
        return health.status in ("healthy", "unknown") if health else False

    def record_request_success(self, provider_name: str):
        if health := self.provider_health.get(provider_name):
            health.record_success()

    def record_request_failure(self, provider_name: str, error: str):
        if health := self.provider_health.get(provider_name):
            health.record_failure(error)

    def get_provider_health(self, provider_name: str) -> Optional[Dict[str, Any]]:
        health = self.provider_health.get(provider_name)
        if not health:
            return None
        return {
            "status": health.status,
            "error_rate": round(health.error_rate, 3),
            "total_requests": health.total_requests,
            "failed_requests": health.failed_requests,
            "last_success": health.last_success.isoformat() if health.last_success else None,
            "last_error": health.last_error,
        }

    def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        return {name: self.get_provider_health(name) for name in self.provider_health}


# Global registry singleton
_registry: Optional[LLMProviderRegistry] = None


def get_provider_registry() -> LLMProviderRegistry:
    global _registry
    if _registry is None:
        _registry = LLMProviderRegistry()
    return _registry


def reset_provider_registry():
    global _registry
    _registry = None
