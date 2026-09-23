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
    
    