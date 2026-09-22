"""
LLM Answer Generation Module
Generates cited answers using retrieved context.
"""

import os
import yaml
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

from retrieve import Retriever

load_dotenv()
logger = logging.getLogger(__name__)


class AnswerGenerator:
    """
    Generates answers using LLM with strict citation requirements.
    
    Features:
    - Multiple LLM provider support (Ollama, OpenAI, Groq)
    - Strict citation format enforcement
    - Automatic refusal when no context available
    - Source tracking
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize generator with retriever and LLM client."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize retriever
        self.retriever = Retriever(config_path)
        
        # LLM settings
        self.llm_config = self.config['llm']
        self.provider = self.llm_config['provider']
        self.model = self.llm_config['model']
        self.temperature = self.llm_config['temperature']
        self.max_tokens = self.llm_config['max_tokens']
        self.system_prompt = self.llm_config['system_prompt']
        
        # Initialize appropriate client
        self.client = self._init_client()
        
        logger.info(f"AnswerGenerator initialized: provider={self.provider}, model={self.model}")
    
    