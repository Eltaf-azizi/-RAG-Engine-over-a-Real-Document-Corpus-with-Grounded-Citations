"""Tests for retrieval module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestRetriever:
    """Test the Retriever class."""
    
    @pytest.fixture
    def retriever(self):
        try:
            from retrieve import Retriever
            return Retriever()
        except Exception:
            pytest.skip("ChromaDB collection not found. Run embed_store.py first.")
    
    def test_search_returns_results(self, retriever):
        """Test that search returns properly formatted results."""
        result = retriever.search("What are fundamental rights?")
        
        assert 'query' in result
        assert 'has_relevant_info' in result
        assert 'top_similarity' in result
        assert 'results' in result
        assert isinstance(result['results'], list)
    
    def test_search_results_have_metadata(self, retriever):
        """Test that results contain required metadata."""
        result = retriever.search("fundamental rights")
        
        if result['results']:
            chunk = result['results'][0]
            assert 'text' in chunk
            assert 'source_file' in chunk
            assert 'page' in chunk
            assert 'similarity' in chunk
    
    def test_irrelevant_query_low_score(self, retriever):
        """Test that unrelated queries get low similarity scores."""
        result = retriever.search("recipe for pizza margherita")
        assert result['top_similarity'] < 0.6, "Unrelated query should have low similarity"
    
    def test_threshold_respected(self, retriever):
        """Test that threshold correctly determines relevance."""
        result = retriever.search("pizza recipe")
        
        if result['top_similarity'] < retriever.threshold:
            assert result['has_relevant_info'] == False
        else:
            assert result['has_relevant_info'] == True