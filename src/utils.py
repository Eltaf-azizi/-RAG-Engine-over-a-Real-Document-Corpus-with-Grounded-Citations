"""Shared utility functions for the RAG system."""

import os
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """Configure logging for the application."""
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"app_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def ensure_directories():
    """Create all necessary directories."""
    directories = [
        "data/documents",
        "data/processed",
        "logs",
        "chroma_db",
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def format_source_citation(source_file: str, page: str) -> str:
    """Format a source citation string."""
    return f"[Source: {source_file}, Page: {page}]"

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent