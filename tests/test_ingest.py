"""Tests for document ingestion module."""

import pytest
import os
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ingest import DocumentLoader


class TestDocumentLoader:
    """Test the DocumentLoader class."""
    
    @pytest.fixture
    def loader(self):
        return DocumentLoader()
    
    @pytest.fixture
    def sample_text(self):
        return "This is a test document. " * 100
    
    def test_chunk_size_configurable(self, loader):
        """Test that chunk size is configurable."""
        assert loader.chunk_size == 500
        loader.chunk_size = 200
        assert loader.chunk_size == 200
    
    def test_split_into_chunks(self, loader, sample_text):
        """Test chunk splitting."""
        chunks = loader._split_into_chunks(sample_text, "test.txt", "1")
        assert len(chunks) > 0
        assert all(len(c['text']) <= loader.chunk_size + 100 for c in chunks)
        assert all(c['source_file'] == "test.txt" for c in chunks)
        assert all(c['page'] == "1" for c in chunks)
    
    def test_chunks_have_required_fields(self, loader, sample_text):
        """Test that chunks have all required metadata fields."""
        chunks = loader._split_into_chunks(sample_text, "test.txt", "1")
        required_fields = ['chunk_id', 'text', 'source_file', 'page', 'start_char', 'end_char']
        
        for chunk in chunks:
            for field in required_fields:
                assert field in chunk, f"Missing field: {field}"
    
    def test_overlap(self, loader):
        """Test that chunks have correct overlap."""
        text = "A" * 1000
        loader.chunk_size = 200
        loader.chunk_overlap = 50
        
        chunks = loader._split_into_chunks(text, "test.txt", "1")
        
        if len(chunks) >= 2:
            # Check overlap
            end_first = chunks[0]['end_char']
            start_second = chunks[1]['start_char']
            assert start_second < end_first, "Chunks should overlap"
    
    def test_min_chunk_length(self, loader):
        """Test that very short texts are filtered out."""
        short_text = "Hi"
        chunks = loader._split_into_chunks(short_text, "test.txt", "1")
        assert len(chunks) == 0