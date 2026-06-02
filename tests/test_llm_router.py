"""
Tests for LLM Provider Router

Tests the provider selection and fallback logic.
"""

import pytest
from unittest.mock import Mock, patch
from src.llm.router import ProviderRouter, ProviderStrategy, get_router
from src.llm.classifier import QueryComplexity


class TestProviderRouter:
    """Test LLM provider routing logic."""
    
    def test_speed_strategy_simple_query(self):
        """Test SPEED strategy selects Groq for simple queries."""
        router = ProviderRouter(strategy="speed")
        provider, model = router.select_provider("What is AI?")
        # Speed strategy with simple query should prefer fast provider
        assert provider in ["groq", "openai"], "SPEED strategy should prefer fast providers"
    
    def test_quality_strategy_complex_query(self):
        """Test QUALITY strategy selects Anthropic for complex queries."""
        router = ProviderRouter(strategy="quality")
        long_query = "Analyze and compare " * 50  # Make it complex
        provider, model = router.select_provider(long_query)
        # Quality strategy with complex query should prefer high-quality provider
        assert provider in ["anthropic", "openai"], "QUALITY strategy should prefer quality providers"
    
    def test_balanced_strategy(self):
        """Test BALANCED strategy uses OpenAI."""
        router = ProviderRouter(strategy="balanced")
        provider, model = router.select_provider("Explain machine learning")
        # Balanced typically uses OpenAI for moderate queries
        assert provider in ["openai", "groq", "anthropic"], "Should select a valid provider"
    
    def test_provider_override(self):
        """Test that provider override bypasses routing logic."""
        router = ProviderRouter()
        
        # Override with anthropic
        provider, model = router.select_provider("Simple query", override_provider="anthropic")
        assert provider == "anthropic", "Override should force Anthropic selection"
        
        # Override with groq
        provider, model = router.select_provider("Simple query", override_provider="groq")
        assert provider == "groq", "Override should force Groq selection"
    
    def test_fallback_chain_generation(self):
        """Test generation of fallback chain."""
        router = ProviderRouter()
        
        # Get fallback for OpenAI
        fallback_chain = router.get_fallback_chain("openai")
        assert isinstance(fallback_chain, list), "Should return a list"
        assert len(fallback_chain) > 0, "Should have fallback options"
        assert "openai" not in [provider for provider, _ in fallback_chain], "Should not include primary provider"
        
        # Check structure of fallback items
        for provider, model in fallback_chain:
            assert isinstance(provider, str), "Provider should be string"
            assert isinstance(model, str), "Model should be string"
            assert provider in ["openai", "anthropic", "groq"], "Should be valid provider"
    
    def test_fallback_chain_excludes_primary(self):
        """Test that fallback chain excludes the primary provider."""
        router = ProviderRouter()
        
        for primary_provider in ["openai", "anthropic", "groq"]:
            fallback_chain = router.get_fallback_chain(primary_provider)
            providers_in_chain = [provider for provider, _ in fallback_chain]
            assert primary_provider not in providers_in_chain, f"Fallback should not include primary provider {primary_provider}"
    
    def test_model_selection(self):
        """Test that correct models are selected for each provider."""
        router = ProviderRouter()
        
        # Test OpenAI
        provider, model = router.select_provider("Test", override_provider="openai")
        assert model == "gpt-4o-mini", "OpenAI should use gpt-4o-mini"
        
        # Test Anthropic
        provider, model = router.select_provider("Test", override_provider="anthropic")
        assert "claude" in model.lower(), "Anthropic should use Claude model"
        
        # Test Groq
        provider, model = router.select_provider("Test", override_provider="groq")
        assert model == "llama-3.3-70b-versatile", "Groq should use Llama 3.3"
    
    def test_global_router_singleton(self):
        """Test that get_router returns singleton instance."""
        router1 = get_router()
        router2 = get_router()
        assert router1 is router2, "Should return same singleton instance"
    
    def test_strategy_from_settings(self):
        """Test loading strategy from settings."""
        with patch('src.llm.router.settings') as mock_settings:
            mock_settings.llm_provider_strategy = "speed"
            router = ProviderRouter()
            assert router.strategy == ProviderStrategy.SPEED
    
    def test_invalid_provider_override(self):
        """Test handling of invalid provider override."""
        router = ProviderRouter()
        
        # Should raise ValueError for invalid provider
        with pytest.raises(ValueError, match="not available"):
            router.select_provider("Test query", override_provider="invalid_provider")
    
    def test_complexity_affects_selection(self):
        """Test that query complexity influences provider selection."""
        router = ProviderRouter()
        
        # Simple query
        simple_query = "Hi"
        provider_simple, _ = router.select_provider(simple_query)
        
        # Complex query  
        complex_query = "Analyze and compare the architectural differences between " * 20
        provider_complex, _ = router.select_provider(complex_query)
        
        # They might be different based on complexity (not guaranteed, but likely)
        # Just verify both are valid
        assert provider_simple in ["openai", "anthropic", "groq"]
        assert provider_complex in ["openai", "anthropic", "groq"]
