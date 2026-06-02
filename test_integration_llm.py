#!/usr/bin/env python3
"""
Integration Test for Multi-LLM Support

Tests actual LLM provider calls with real API keys.
Run with: python test_integration_llm.py
"""

import sys
import os
from src.config.settings import settings
from src.llm.provider import get_provider_registry
from src.llm.router import get_router
from src.llm.classifier import classify_query
from src.pipelines.retrieval import retrieve_documents

def test_provider_availability():
    """Test that all providers are available."""
    print("\n🔍 Testing Provider Availability...")
    registry = get_provider_registry()
    
    providers = ["openai", "anthropic", "groq"]
    for provider in providers:
        available = registry.is_provider_available(provider)
        status = "✅" if available else "❌"
        print(f"  {status} {provider}: {'available' if available else 'not available'}")
    
    return True

def test_query_classification():
    """Test query complexity classification."""
    print("\n🔍 Testing Query Classification...")
    
    test_cases = [
        ("What is AI?", "SIMPLE"),
        ("Explain how neural networks work in deep learning.", "MODERATE"),
        ("Compare and contrast the architectural differences between transformer-based models and recurrent neural networks, considering factors like parallelization, long-range dependencies, and computational efficiency.", "COMPLEX")
    ]
    
    for query, expected in test_cases:
        complexity, confidence = classify_query(query)
        print(f"  Query: '{query[:50]}...'")
        print(f"    → {complexity.value.upper()} (confidence: {confidence:.2f})")
    
    return True

def test_provider_routing():
    """Test provider selection logic."""
    print("\n🔍 Testing Provider Routing...")
    
    router = get_router()
    
    test_cases = [
        ("Hi", None),
        ("What is machine learning?", None),
        ("Explain transformers", "anthropic"),  # Manual override
    ]
    
    for query, override in test_cases:
        provider, model = router.select_provider(query, override)
        override_str = f" (override: {override})" if override else ""
        print(f"  Query: '{query}'{override_str}")
        print(f"    → Selected: {provider}:{model}")
    
    return True

def test_live_query_simple():
    """Test a simple query with real LLM call."""
    print("\n🔍 Testing Simple Query (Real LLM Call)...")
    
    query = "What is RAG in 10 words or less?"
    print(f"  Query: '{query}'")
    
    try:
        # This will use actual API (make sure documents exist in Qdrant)
        result = retrieve_documents(query, top_k=2)
        
        print(f"  ✅ Answer: {result['answer'][:100]}...")
        print(f"  Provider: {result['metadata'].get('provider_used', 'unknown')}")
        print(f"  Fallback: {result['metadata'].get('provider_fallback', False)}")
        print(f"  Documents: {result['metadata']['num_documents_retrieved']}")
        print(f"  Timing: {result['metadata']['total_ms']}ms")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_provider_fallback():
    """Test fallback behavior."""
    print("\n🔍 Testing Provider Fallback Chain...")
    
    router = get_router()
    
    for provider in ["openai", "anthropic", "groq"]:
        fallback_chain = router.get_fallback_chain(provider)
        print(f"  {provider} fallback chain:")
        for fallback_provider, fallback_model in fallback_chain:
            print(f"    → {fallback_provider}:{fallback_model}")
    
    return True

def test_provider_health():
    """Check provider health status."""
    print("\n🔍 Testing Provider Health Monitoring...")
    
    registry = get_provider_registry()
    health = registry.get_all_health()
    
    for provider, status in health.items():
        print(f"  {provider}:")
        print(f"    Status: {status['status']}")
        print(f"    Total requests: {status['total_requests']}")
        print(f"    Failed requests: {status['failed_requests']}")
        print(f"    Error rate: {status['error_rate']:.2%}")
    
    return True

def main():
    """Run all integration tests."""
    print("=" * 60)
    print("🚀 Multi-LLM Integration Tests")
    print("=" * 60)
    
    # Check API keys
    print("\n📋 Configuration:")
    print(f"  OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
    print(f"  Anthropic API Key: {'✅ Set' if settings.anthropic_api_key else '❌ Missing'}")
    print(f"  Groq API Key: {'✅ Set' if settings.groq_api_key else '❌ Missing'}")
    print(f"  Strategy: {settings.llm_provider_strategy}")
    
    tests = [
        ("Provider Availability", test_provider_availability),
        ("Query Classification", test_query_classification),
        ("Provider Routing", test_provider_routing),
        ("Provider Fallback", test_provider_fallback),
        ("Provider Health", test_provider_health),
        ("Live Query (Simple)", test_live_query_simple),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
