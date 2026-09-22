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
    
    def _init_client(self):
        """Initialize the appropriate LLM client based on provider."""
        from openai import OpenAI
        
        if self.provider == 'ollama':
            return OpenAI(
                base_url=self.llm_config.get('api_base', 'http://localhost:11434/v1'),
                api_key='ollama'
            )
        elif self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            return OpenAI(api_key=api_key)
        elif self.provider == 'groq':
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            return OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )
        else:
            # Generic OpenAI-compatible API
            return OpenAI(
                base_url=self.llm_config.get('api_base'),
                api_key=os.getenv('API_KEY', 'dummy')
            )
    
    def _build_prompt(self, query: str, context: str, has_context: bool) -> str:
        """
        Build the prompt for the LLM with strict rules.
        
        Args:
            query: User's question
            context: Formatted context from retrieved chunks
            has_context: Whether relevant context was found
            
        Returns:
            Complete prompt string
        """
        if not has_context:
            return f"""You are a constitutional law expert assistant.

I need to answer this question: "{query}"

Unfortunately, I searched through all available constitutional documents and could not find any relevant information to answer this question.

CRITICAL INSTRUCTION: You MUST respond with EXACTLY this phrase and nothing else:
"I don't have enough information in the provided documents to answer this question."

Do not add explanations, apologies, or suggestions."""
        
        return f"""{self.system_prompt}

CONTEXT FROM CONSTITUTIONAL DOCUMENTS:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Answer using ONLY the information from the context above
2. Cite EVERY fact using this format: [Source: filename, Page: X]
3. If the context partially answers the question, state what you know and what's missing
4. Do NOT use any outside knowledge or training data
5. Be concise, factual, and well-organized

ANSWER:"""
    
    def _format_sources(self, search_results: Dict) -> List[Dict]:
        """
        Extract formatted source information from search results.
        
        Args:
            search_results: Output from retriever.search()
            
        Returns:
            List of source dictionaries
        """
        sources = []
        seen = set()
        
        for r in search_results.get('results', []):
            key = (r['source_file'], r['page'])
            if key not in seen:
                sources.append({
                    'source_file': r['source_file'],
                    'page': r['page'],
                    'similarity': r['similarity'],
                    'excerpt': r['text'][:200] + "..."
                })
                seen.add(key)
        
        return sources
    
    