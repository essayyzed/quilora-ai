"""
Provider Router

Intelligent LLM provider selection with fallback chain support.
"""

from typing import Optional, List, Tuple
from enum import Enum
import logging
from src.llm.provider import get_provider_registry
from src.llm.classifier import QueryComplexity, classify_query
from src.config.settings import settings

logger = logging.getLogger(__name__)


class ProviderStrategy(str, Enum):
    """Provider selection strategies."""
    SPEED = "speed"       # Prioritize fast, cheap providers
    BALANCED = "balanced"  # Balance speed and quality
    QUALITY = "quality"    # Prioritize quality over cost


class ProviderRouter:
    """
    Routes queries to optimal LLM provider based on complexity and strategy.
    
    Implements intelligent provider selection with automatic fallback chain.
    """
    
    def __init__(self, strategy: str = None):
        """
        Initialize router with strategy.
        
        Args:
            strategy: "speed", "balanced", or "quality" (defaults to settings)
        """
        strategy_str = strategy or settings.llm_provider_strategy
        try:
            self.strategy = ProviderStrategy(strategy_str)
        except ValueError:
            logger.warning(f"Invalid strategy '{strategy_str}', defaulting to 'balanced'")
            self.strategy = ProviderStrategy.BALANCED
        
        self.registry = get_provider_registry()
        
    def select_provider(
        self,
        query: str,
        override_provider: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Select optimal provider for query.
        
        Args:
            query: User's question
            override_provider: Optional manual provider selection
            
        Returns:
            Tuple of (provider_name, model_string)
            
        Raises:
            ValueError: If override provider is invalid or no providers available
        """
        # Handle manual override
        if override_provider:
            if not self.registry.is_provider_available(override_provider):
                available = self.registry.get_available_providers()
                raise ValueError(
                    f"Provider '{override_provider}' not available. "
                    f"Available: {', '.join(available)}"
                )
            
            model = self._get_model_for_provider(override_provider)
            logger.info(
                f"Provider override: {override_provider}:{model} "
                f"(manual selection)"
            )
            return override_provider, model
        
        # Classify query complexity
        complexity, confidence = classify_query(query)
        
        # Select provider based on strategy and complexity
        provider_name = self._route_by_strategy_and_complexity(complexity)
        
        if not provider_name:
            raise ValueError("No LLM providers available")
        
        model = self._get_model_for_provider(provider_name)
        
        logger.info(
            f"Provider selected: {provider_name}:{model} "
            f"(strategy={self.strategy.value}, complexity={complexity.value}, "
            f"confidence={confidence:.2f})"
        )
        
        return provider_name, model
    
    def get_fallback_chain(self, primary_provider: str) -> List[Tuple[str, str]]:
        """
        Get fallback provider chain for a primary provider.
        
        Args:
            primary_provider: The initially selected provider
            
        Returns:
            List of (provider_name, model) tuples in fallback order
        """
        # Define fallback chains based on strategy
        fallback_chains = {
            ProviderStrategy.SPEED: ["groq", "openai", "anthropic"],
            ProviderStrategy.BALANCED: ["openai", "groq", "anthropic"],
            ProviderStrategy.QUALITY: ["anthropic", "openai", "groq"],
        }
        
        chain = fallback_chains[self.strategy]
        
        # Remove primary from chain and filter to available providers
        fallback_order = [p for p in chain if p != primary_provider]
        result = []
        
        for provider_name in fallback_order:
            if self.registry.is_provider_available(provider_name):
                model = self._get_model_for_provider(provider_name)
                result.append((provider_name, model))
        
        if result:
            logger.debug(
                f"Fallback chain for {primary_provider}: "
                f"{', '.join(f'{p}:{m}' for p, m in result)}"
            )
        
        return result
    
    def _route_by_strategy_and_complexity(
        self,
        complexity: QueryComplexity
    ) -> Optional[str]:
        """
        Select provider based on strategy and query complexity.
        
        Returns:
            Provider name or None if no providers available
        """
        # Define preference matrix [strategy][complexity] -> provider priority
        preferences = {
            ProviderStrategy.SPEED: {
                QueryComplexity.SIMPLE: ["groq", "openai", "anthropic"],
                QueryComplexity.MODERATE: ["groq", "openai", "anthropic"],
                QueryComplexity.COMPLEX: ["openai", "anthropic", "groq"],
            },
            ProviderStrategy.BALANCED: {
                QueryComplexity.SIMPLE: ["groq", "openai", "anthropic"],
                QueryComplexity.MODERATE: ["openai", "groq", "anthropic"],
                QueryComplexity.COMPLEX: ["anthropic", "openai", "groq"],
            },
            ProviderStrategy.QUALITY: {
                QueryComplexity.SIMPLE: ["openai", "anthropic", "groq"],
                QueryComplexity.MODERATE: ["anthropic", "openai", "groq"],
                QueryComplexity.COMPLEX: ["anthropic", "openai", "groq"],
            },
        }
        
        priority_list = preferences[self.strategy][complexity]
        
        # Return first available provider from priority list
        for provider_name in priority_list:
            if self.registry.is_provider_available(provider_name):
                return provider_name
        
        # Fallback: return any available provider
        available = self.registry.get_available_providers()
        return available[0] if available else None
    
    def _get_model_for_provider(self, provider_name: str) -> str:
        """
        Get configured model string for provider.
        
        Returns:
            Model name (e.g., "llama-3.3-70b-versatile", "gpt-4o-mini")
        """
        model_map = {
            "groq": settings.primary_llm_provider,
            "openai": settings.fallback_llm_provider,
            "anthropic": settings.premium_llm_provider,
        }
        
        model_string = model_map.get(provider_name, "")
        
        # Extract model name from "provider:model" format
        if ":" in model_string:
            return model_string.split(":", 1)[1]
        
        return model_string


# Global router instance
_router: Optional[ProviderRouter] = None


def get_router(strategy: str = None) -> ProviderRouter:
    """
    Get or create global router singleton.
    
    Args:
        strategy: Optional strategy override
        
    Returns:
        ProviderRouter: Configured router instance
    """
    global _router
    if _router is None or (strategy and strategy != _router.strategy.value):
        _router = ProviderRouter(strategy)
    return _router


def reset_router():
    """Reset global router (for testing)."""
    global _router
    _router = None
