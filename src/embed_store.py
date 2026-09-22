"""
Embedding and Vector Store Module
Generates embeddings and stores them in ChromaDB.
"""

import os
import yaml
import logging
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import numpy as np
from tqdm import tqdm

from ingest import DocumentLoader

logger = logging.getLogger(__name__)


class EmbeddingStore:
    """
    Handles embedding generation and ChromaDB storage.
    
    Features:
    - Local embedding model (sentence-transformers)
    - Batch embedding generation
    - Persistent ChromaDB storage
    - Collection management
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize embedding model and vector store."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Embedding settings
        embed_config = self.config['embedding']
        self.model_name = embed_config['model_name']
        self.batch_size = embed_config['batch_size']
        self.device = embed_config['device']
        
        # Vector store settings
        vs_config = self.config['vector_store']
        self.persist_directory = vs_config['persist_directory']
        self.collection_name = vs_config['collection_name']
        
        # Load embedding model
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        logger.info(f"Model loaded. Dimension: {self.model.get_sentence_embedding_dimension()}")
        
        # Initialize ChromaDB
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        logger.info(f"ChromaDB initialized at: {self.persist_directory}")
    
    def reset_collection(self):
        """Delete and recreate the collection (fresh start)."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted existing collection: {self.collection_name}")
        except Exception:
            pass
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Created new collection: {self.collection_name}")
    
    def get_or_create_collection(self):
        """Get existing collection or create new one."""
        try:
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name} ({self.collection.count()} chunks)")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    