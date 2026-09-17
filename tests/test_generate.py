"""Tests for answer generation module."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestAnswerGenerator:
    """Test the AnswerGenerator class."""
    
    @pytest.fixture
    def generator(self):
        try:
            from generate import AnswerGenerator
            return AnswerGenerator()
        except Exception:
            pytest.skip("LLM not available or config missing.")
    
    def test_answer_has_required_fields(self, generator):
        """Test that answer returns all required fields."""
        result = generator.answer("What are fundamental rights?")
        
        required_fields = ['query', 'answer', 'sources', 'has_relevant_info', 
                          'top_similarity', 'threshold']
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_refusal_on_irrelevant_query(self, generator):
        """Test that system refuses on clearly irrelevant queries."""
        result = generator.answer("What is the recipe for chocolate chip cookies?")
        
        assert "don't have enough information" in result['answer'].lower() or \
               result['has_relevant_info'] == False
    
    def test_build_prompt_has_context(self, generator):
        """Test prompt building with context."""
        prompt = generator._build_prompt(
            "Test question?",
            "Sample context text",
            True
        )
        
        assert "Test question?" in prompt
        assert "Sample context text" in prompt
    
    def test_build_prompt_no_context(self, generator):
        """Test prompt building without context."""
        prompt = generator._build_prompt(
            "Test question?",
            "",
            False
        )
        
        assert "don't have enough information" in prompt.lower()
    
    def test_format_sources(self, generator):
        """Test source formatting."""
        mock_results = {
            'results': [
                {
                    'source_file': 'test.pdf',
                    'page': '5',
                    'similarity': 0.95,
                    'text': 'Sample text for testing purposes.'
                }
            ]
        }
        
        sources = generator._format_sources(mock_results)
        
        assert len(sources) == 1
        assert sources[0]['source_file'] == 'test.pdf'
        assert sources[0]['page'] == '5'
        assert sources[0]['similarity'] == 0.95