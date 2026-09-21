"""
Retrieval Module
Semantic search over constitutional documents with similarity threshold.
"""

import yaml
import logging
from sentence_transformers import SentenceTransformer
import chromadb
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class Retriever:
    """
    Semantic search and retrieval over the document corpus.
    
    Features:
    - Query embedding generation
    - Similarity-based retrieval
    - Configurable threshold for relevance
    - Source metadata preservation
    """
    
    