"""
Tests for Query Complexity Classifier

Tests the heuristic-based query classification system.
"""

import pytest
from src.llm.classifier import QueryComplexityClassifier, QueryComplexity, classify_query


class TestQueryComplexityClassifier:
    """Test query complexity classification."""
    
    def test_simple_query(self):
        """Test classification of simple queries."""
        classifier = QueryComplexityClassifier()
        
        simple_queries = [
            "What is RAG?",
            "Hello",
            "Define AI",
            "Who are you?"
        ]
        
        for query in simple_queries:
            complexity, confidence = classifier.classify(query)
            assert complexity == QueryComplexity.SIMPLE, f"'{query}' should be SIMPLE"
            assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
    
    def test_moderate_query(self):
        """Test classification of moderate complexity queries."""
        classifier = QueryComplexityClassifier()
        
        moderate_queries = [
            "How does retrieval-augmented generation work in practice?",
            "What are the main differences between GPT-3 and GPT-4?",
            "Explain the benefits of using vector databases for semantic search."
        ]
        
        for query in moderate_queries:
            complexity, confidence = classifier.classify(query)
            assert complexity == QueryComplexity.MODERATE, f"'{query}' should be MODERATE"
            assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
    
    def test_complex_query(self):
        """Test classification of complex queries."""
        classifier = QueryComplexityClassifier()
        
        complex_queries = [
            "Compare and contrast the architectural differences between traditional search engines and modern RAG systems, "
            "considering factors like latency, accuracy, scalability, and cost-effectiveness. How do these trade-offs "
            "affect production deployment decisions?",
            "Analyze the theoretical foundations of transformer architectures and explain how attention mechanisms enable "
            "cross-modal learning across text, image, and audio modalities.",
            "What are the implications of fine-tuning large language models on domain-specific data? How does this compare "
            "to using retrieval-augmented generation? What are the computational and financial trade-offs?"
        ]
        
        for query in complex_queries:
            complexity, confidence = classifier.classify(query)
            assert complexity == QueryComplexity.COMPLEX, f"'{query}' should be COMPLEX"
            assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
    
    def test_keyword_detection(self):
        """Test that complexity keywords influence classification."""
        classifier = QueryComplexityClassifier()
        
        # Short query with complexity keywords should rank higher
        query_with_keywords = "Compare and analyze transformer architectures"
        complexity, _ = classifier.classify(query_with_keywords)
        
        # This should be at least MODERATE due to keywords
        assert complexity in [QueryComplexity.MODERATE, QueryComplexity.COMPLEX]
    
    def test_multi_question_detection(self):
        """Test detection of multiple questions."""
        classifier = QueryComplexityClassifier()
        
        multi_question = "What is RAG? How does it work? Why is it better?"
        complexity, _ = classifier.classify(multi_question)
        
        # Multiple questions should increase complexity
        assert complexity in [QueryComplexity.MODERATE, QueryComplexity.COMPLEX]
    
    def test_global_classify_function(self):
        """Test the global classify_query helper function."""
        complexity, confidence = classify_query("What is machine learning?")
        assert isinstance(complexity, QueryComplexity)
        assert 0 <= confidence <= 1
    
    def test_empty_query(self):
        """Test handling of empty queries."""
        classifier = QueryComplexityClassifier()
        complexity, confidence = classifier.classify("")
        assert complexity == QueryComplexity.SIMPLE
        assert confidence >= 0
    
    def test_whitespace_query(self):
        """Test handling of whitespace-only queries."""
        classifier = QueryComplexityClassifier()
        complexity, confidence = classifier.classify("   \n\t  ")
        assert complexity == QueryComplexity.SIMPLE
