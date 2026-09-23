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
    
    
    def load_document(self, filepath: str) -> str:
        """Load document based on extension."""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.pdf':
            return self.load_pdf(filepath)
        elif ext in ['.txt', '.md', '.markdown']:
            return self.load_text_file(filepath)
        else:
            raise ValueError(f"Unsupported format: {ext}")
    
    def chunk_text(self, text: str, source_file: str) -> List[Dict]:
        """
        Split document text into overlapping chunks with metadata.
        
        Args:
            text: Full document text with page markers
            source_file: Source filename for metadata
            
        Returns:
            List of chunk dictionaries with text, source, and page info
        """
        chunks = []
        
        if "[PAGE_" not in text:
            # No page markers, treat as single page
            return self._split_into_chunks(text, source_file, "1")
        
        # Split by page markers
        sections = text.split("[PAGE_")
        
        for section in sections:
            if not section.strip():
                continue
            
            try:
                # Extract page number
                end_bracket = section.index(']')
                page_num = section[:end_bracket].strip()
                content = section[end_bracket + 1:].strip()
                
                if content and len(content) >= self.min_chunk_length:
                    page_chunks = self._split_into_chunks(content, source_file, page_num)
                    chunks.extend(page_chunks)
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parsing page section: {e}")
                continue
        
        logger.info(f"Created {len(chunks)} chunks from {source_file}")
        return chunks
    
    def _split_into_chunks(self, text: str, source_file: str, page: str) -> List[Dict]:
        """
        Split text into overlapping chunks with sentence boundary awareness.
        
        Args:
            text: Text to chunk
            source_file: Source filename
            page: Page number
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        text = text.strip()
        
        if len(text) < self.min_chunk_length:
            return chunks
        
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                # Last chunk
                chunk_text = text[start:].strip()
            else:
                # Find good break point
                # Priority: sentence boundary > paragraph > word
                search_end = min(end + 100, len(text))
                search_start = max(end - 100, start + self.min_chunk_length)
                
                # Try sentence boundaries
                for i in range(search_end - 1, search_start, -1):
                    if text[i] in '.!?':
                        if i + 1 < len(text) and text[i + 1] in ' \n':
                            end = i + 1
                            break
                else:
                    # Try paragraph break
                    for i in range(search_end - 1, search_start, -1):
                        if text[i:i+2] == '\n\n':
                            end = i
                            break
                    else:
                        # Try word boundary
                        for i in range(search_end - 1, search_start, -1):
                            if text[i] == ' ':
                                end = i
                                break
            
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) >= self.min_chunk_length:
                chunks.append({
                    'chunk_id': f"{source_file}_p{page}_c{chunk_index}",
                    'text': chunk_text,
                    'source_file': source_file,
                    'page': page,
                    'start_char': start,
                    'end_char': end,
                    'chunk_index': chunk_index
                })
                chunk_index += 1
            
            start = end - self.chunk_overlap
        
        return chunks
    
    