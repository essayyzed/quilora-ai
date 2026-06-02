"""
Tests for LLM Provider Registry

Tests provider health tracking and client management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm.provider import LLMProviderRegistry, ProviderHealth, get_provider_registry


class TestProviderHealth:
    """Test ProviderHealth dataclass."""
    
    def test_health_initialization(self):
        """Test ProviderHealth default values."""
        health = ProviderHealth()
        assert health.status == "unknown"
        assert health.error_rate == 0.0
        assert health.total_requests == 0
        assert health.failed_requests == 0
        assert health.last_success is None
        assert health.last_error is None


class TestLLMProviderRegistry:
    """Test LLM provider registry functionality."""
    
    @patch('src.llm.provider.aisuite.Client')
    def test_registry_initialization(self, mock_client_class):
        """Test that registry initializes with aisuite client."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        registry = LLMProviderRegistry()
        assert registry.client is not None
        assert "openai" in registry.provider_health
        assert "anthropic" in registry.provider_health
        assert "groq" in registry.provider_health
    
    @patch('src.llm.provider.aisuite.Client')
    def test_record_success(self, mock_client_class):
        """Test recording successful requests."""
        registry = LLMProviderRegistry()
        
        # Record success for OpenAI
        registry.record_request_success("openai")
        
        health = registry.provider_health["openai"]
        assert health.status == "healthy"
        assert health.total_requests == 1
        assert health.failed_requests == 0
        assert health.error_rate == 0.0
        assert health.last_success is not None
    
    @patch('src.llm.provider.aisuite.Client')
    def test_record_failure(self, mock_client_class):
        """Test recording failed requests."""
        registry = LLMProviderRegistry()
        
        # Record failure for Anthropic
        registry.record_request_failure("anthropic", "Connection timeout")
        
        health = registry.provider_health["anthropic"]
        assert health.status == "unhealthy"
        assert health.total_requests == 1
        assert health.failed_requests == 1
        assert health.error_rate == 1.0
        assert health.last_error == "Connection timeout"
    
    @patch('src.llm.provider.aisuite.Client')
    def test_error_rate_calculation(self, mock_client_class):
        """Test error rate is calculated correctly."""
        registry = LLMProviderRegistry()
        
        # Record mix of success and failures
        registry.record_request_success("groq")
        registry.record_request_success("groq")
        registry.record_request_failure("groq", "Error 1")
        registry.record_request_success("groq")
        
        health = registry.provider_health["groq"]
        assert health.total_requests == 4
        assert health.failed_requests == 1
        assert health.error_rate == 0.25  # 1 failure out of 4 requests
    
    @patch('src.llm.provider.aisuite.Client')
    def test_get_provider_health(self, mock_client_class):
        """Test retrieving health for specific provider."""
        registry = LLMProviderRegistry()
        
        registry.record_request_success("openai")
        health_dict = registry.get_provider_health("openai")
        
        assert "status" in health_dict
        assert "error_rate" in health_dict
        assert "total_requests" in health_dict
        assert health_dict["status"] == "healthy"
    
    @patch('src.llm.provider.aisuite.Client')
    def test_get_all_health(self, mock_client_class):
        """Test retrieving health for all providers."""
        registry = LLMProviderRegistry()
        
        all_health = registry.get_all_health()
        
        assert isinstance(all_health, dict)
        assert "openai" in all_health
        assert "anthropic" in all_health
        assert "groq" in all_health
        
        # Check structure of each provider's health
        for provider, health in all_health.items():
            assert "status" in health
            assert "error_rate" in health
            assert "total_requests" in health
    
    @patch('src.llm.provider.aisuite.Client')
    def test_status_transitions(self, mock_client_class):
        """Test that status transitions between healthy/unhealthy correctly."""
        registry = LLMProviderRegistry()
        
        # Start unknown
        assert registry.provider_health["openai"].status == "unknown"
        
        # Success -> healthy
        registry.record_request_success("openai")
        assert registry.provider_health["openai"].status == "healthy"
        
        # Failure -> unhealthy
        registry.record_request_failure("openai", "Error")
        assert registry.provider_health["openai"].status == "unhealthy"
        
        # Success -> healthy again
        registry.record_request_success("openai")
        assert registry.provider_health["openai"].status == "healthy"
    
    @patch('src.llm.provider.aisuite.Client')
    def test_global_registry_singleton(self, mock_client_class):
        """Test that get_provider_registry returns singleton."""
        registry1 = get_provider_registry()
        registry2 = get_provider_registry()
        assert registry1 is registry2, "Should return same singleton instance"
    
    @patch('src.llm.provider.aisuite.Client')
    def test_concurrent_requests_tracking(self, mock_client_class):
        """Test that concurrent requests are tracked correctly."""
        registry = LLMProviderRegistry()
        
        # Simulate concurrent requests to different providers
        registry.record_request_success("openai")
        registry.record_request_success("anthropic")
        registry.record_request_success("groq")
        
        assert registry.provider_health["openai"].total_requests == 1
        assert registry.provider_health["anthropic"].total_requests == 1
        assert registry.provider_health["groq"].total_requests == 1
    
    @patch('src.llm.provider.aisuite.Client')
    def test_unknown_provider(self, mock_client_class):
        """Test handling of unknown provider."""
        registry = LLMProviderRegistry()
        
        # Should handle gracefully or ignore unknown provider
        registry.record_request_success("unknown_provider")
        
        # Unknown provider shouldn't be in tracked providers
        assert "unknown_provider" not in registry.provider_health or \
               registry.provider_health.get("unknown_provider").status == "unknown"
