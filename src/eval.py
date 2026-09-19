"""
Evaluation Module
Measures retrieval hit-rate and refusal behavior.
"""

import json
import yaml
import logging
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path

from retrieve import Retriever
from generate import AnswerGenerator

logger = logging.getLogger(__name__)


class Evaluator:
    """
    Evaluates the RAG system against the Definition of Done.
    
    Metrics:
    - Retrieval hit-rate (target: ≥80%)
    - Refusal rate on out-of-scope questions
    - Source citation accuracy
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize evaluator with config and components."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.eval_config = self.config['evaluation']
        self.target_hit_rate = self.eval_config['target_hit_rate']
        
        # Initialize components
        self.retriever = Retriever(config_path)
        
        try:
            self.generator = AnswerGenerator(config_path)
            self.llm_available = True
        except Exception as e:
            logger.warning(f"LLM not available: {e}. Running retrieval-only evaluation.")
            self.llm_available = False
        
        # Load evaluation questions
        questions_file = self.eval_config['questions_file']
        with open(questions_file, 'r') as f:
            self.eval_data = json.load(f)
        
        self.questions = self.eval_data['questions']
        self.out_of_scope = self.eval_config.get('out_of_scope_questions', [
            "What is the recipe for chocolate cake?",
            "How do I fix a flat tire?",
            "Who won the 1998 World Cup?",
            "How does nuclear fusion work?",
            "What is the capital of Brazil?"
        ])
        
        logger.info(f"Evaluator initialized: {len(self.questions)} questions, "
                   f"LLM available: {self.llm_available}")
    
    