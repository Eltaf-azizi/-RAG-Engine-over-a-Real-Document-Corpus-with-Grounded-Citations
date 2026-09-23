"""
Document Ingestion Module
Loads PDF/Markdown files, extracts text, and chunks with metadata.
"""

import os
import json
import yaml
import PyPDF2
import logging
from typing import List, Dict, Optional
from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Handles document loading and chunking for the RAG system.
    
    Features:
    - Loads PDF and text files
    - Preserves page numbers
    - Configurable chunk size and overlap
    - Sentence-boundary-aware splitting
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        ingestion_config = self.config['ingestion']
        self.chunk_size = ingestion_config['chunk_size']
        self.chunk_overlap = ingestion_config['chunk_overlap']
        self.min_chunk_length = ingestion_config['min_chunk_length']
        self.data_directory = ingestion_config['data_directory']
        self.supported_formats = ingestion_config['supported_formats']
        
        logger.info(f"DocumentLoader initialized: chunk_size={self.chunk_size}, "
                   f"overlap={self.chunk_overlap}")

    
    def load_pdf(self, filepath: str) -> str:
        """
        Extract text from PDF with page markers.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Extracted text with [PAGE_X] markers
        """
        logger.info(f"Loading PDF: {filepath}")
        text_parts = []
        total_pages = 0
        
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                
                for page_num in range(total_pages):
                    try:
                        page = reader.pages[page_num]
                        page_text = page.extract_text()
                        
                        if page_text and page_text.strip():
                            text_parts.append(f"[PAGE_{page_num + 1}]\n{page_text.strip()}")
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num + 1}: {e}")
                        continue
                
            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {total_pages} pages, {len(full_text)} characters")
            return full_text
            
        except Exception as e:
            logger.error(f"Failed to load PDF {filepath}: {e}")
            raise
    
    def load_text_file(self, filepath: str) -> str:
        """Load plain text or markdown file."""
        logger.info(f"Loading text file: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Add page markers based on newlines (rough estimate: 3000 chars per page)
        pages = []
        chars_per_page = 3000
        for i in range(0, len(text), chars_per_page):
            page_num = (i // chars_per_page) + 1
            chunk = text[i:i + chars_per_page]
            pages.append(f"[PAGE_{page_num}]\n{chunk}")
        
        return "\n\n".join(pages)
    
    