"""
Query Complexity Classifier

Analyzes query text to determine complexity level (simple/moderate/complex)
for intelligent LLM provider routing.
"""

from typing import Tuple, Optional
from enum import Enum
import re
import logging
from src.config.settings import settings

logger = logging.getLogger(__name__)


class QueryComplexity(str, Enum):
    """Query complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class QueryComplexityClassifier:
    """
    Classifies queries by complexity using heuristics.
    
    Analysis factors:
    - Word count
    - Question count (multiple questions = higher complexity)
    - Technical keywords
    - Reasoning indicators (analyze, compare, explain, etc.)
    - Sentence structure
    """
    
    # Keywords that indicate complex reasoning requirements
    COMPLEX_KEYWORDS = {
        "analyze", "analysis", "compare", "contrast", "evaluate", "assess",
        "explain", "justify", "implications", "consequences", "relationship",
        "synthesis", "critique", "interpret", "demonstrate", "elaborate",
        "distinguish", "differentiate", "investigate", "examine", "difference",
    }

    # Keywords that indicate technical/specialized knowledge
    TECHNICAL_KEYWORDS = {
        "algorithm", "architecture", "implementation", "optimization",
        "infrastructure", "methodology", "framework", "paradigm",
        "protocol", "specification", "configuration", "deployment",
        "retrieval", "embedding", "vector", "semantic", "transformer",
        "augmented", "generation", "gpt", "llm",
    }
    
    def __init__(
        self,
        simple_max_words: int = None,
        moderate_max_words: int = None
    ):
        """
        Initialize classifier with configurable thresholds.
        
        Args:
            simple_max_words: Max words for simple classification (default from settings)
            moderate_max_words: Max words for moderate classification (default from settings)
        """
        self.simple_max_words = simple_max_words or settings.llm_complexity_simple_max_words
        self.moderate_max_words = moderate_max_words or settings.llm_complexity_moderate_max_words
    
    def classify(self, query: str) -> Tuple[QueryComplexity, float]:
        """
        Classify query complexity.
        
        Args:
            query: User's question text
            
        Returns:
            Tuple of (complexity_level, confidence_score)
        """
        if not query or not query.strip():
            return QueryComplexity.SIMPLE, 1.0
        
        query_lower = query.lower()
        words = query.split()
        word_count = len(words)
        
        # Count sentences/questions
        question_marks = query.count("?")
        sentences = len(re.split(r'[.!?]+', query))
        
        # Check for complex keywords
        has_complex_keywords = any(kw in query_lower for kw in self.COMPLEX_KEYWORDS)
        has_technical_keywords = any(kw in query_lower for kw in self.TECHNICAL_KEYWORDS)
        
        # Check for multi-part questions
        has_multiple_questions = question_marks > 1 or any(
            marker in query_lower for marker in ["first", "second", "also", "additionally"]
        )
        
        # Scoring system
        complexity_score = 0
        confidence_factors = []
        
        # Word count factor (most important)
        if word_count <= self.simple_max_words:
            complexity_score += 0
            confidence_factors.append(0.9)  # High confidence in simple
        elif word_count <= self.moderate_max_words:
            complexity_score += 1
            confidence_factors.append(0.8)  # Good confidence in moderate
        else:
            complexity_score += 2
            confidence_factors.append(0.85)  # Good confidence in complex
        
        # Additional complexity indicators — count each matching keyword individually
        complex_keyword_matches = sum(1 for kw in self.COMPLEX_KEYWORDS if kw in query_lower)
        if complex_keyword_matches >= 2:
            complexity_score += 1.5
            confidence_factors.append(0.75)
        elif complex_keyword_matches == 1:
            complexity_score += 0.75
            confidence_factors.append(0.7)

        if has_technical_keywords:
            complexity_score += 1
            confidence_factors.append(0.6)

        if has_multiple_questions:
            complexity_score += 1
            confidence_factors.append(0.75)

        if sentences > 3:
            complexity_score += 0.5
            confidence_factors.append(0.65)

        # Determine final complexity
        if complexity_score >= 2:
            result = QueryComplexity.COMPLEX
            confidence = max(confidence_factors) if confidence_factors else 0.7
        elif complexity_score >= 0.75:
            result = QueryComplexity.MODERATE
            confidence = max(confidence_factors) if confidence_factors else 0.75
        else:
            result = QueryComplexity.SIMPLE
            confidence = max(confidence_factors) if confidence_factors else 0.85
        
        logger.debug(
            f"Query classified: complexity={result.value}, confidence={confidence:.2f}, "
            f"word_count={word_count}, score={complexity_score}"
        )
        
        return result, confidence


# Global classifier instance
_classifier: Optional[QueryComplexityClassifier] = None


def get_classifier() -> QueryComplexityClassifier:
    """Get or create global classifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = QueryComplexityClassifier()
    return _classifier


def classify_query(query: str) -> Tuple[QueryComplexity, float]:
    """
    Convenience function to classify a query.
    
    Args:
        query: User's question text
        
    Returns:
        Tuple of (complexity_level, confidence_score)
    """
    classifier = get_classifier()
    return classifier.classify(query)
