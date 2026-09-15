"""
Streamlit UI for Constitutional RAG Q&A System
"""

import streamlit as st
import yaml
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generate import AnswerGenerator

# Page configuration
st.set_page_config(
    page_title="Constitutional RAG Q&A",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
    }
    .sub-header {
        font-size: 1rem;
        color: #6b7280;
    }
    .source-box {
        background-color: #f3f4f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .citation {
        color: #2563eb;
        font-weight: bold;
    }
    .warning-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    .refusal-box {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    .success-box {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_generator():
    """Load the answer generator (cached)."""
    try:
        return AnswerGenerator()
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")
        st.info("Make sure you've run the ingestion pipeline first:")
        st.code("python src/embed_store.py", language="bash")
        return None


@st.cache_resource
def load_config():
    """Load configuration."""
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)


def display_source(source, index):
    """Display a single source with formatting."""
    with st.expander(
        f"📄 Source {index}: {source['source_file']} — Page {source['page']} "
        f"(Relevance: {source['similarity']:.1%})"
    ):
        st.markdown(f"**File:** `{source['source_file']}`")
        st.markdown(f"**Page:** {source['page']}")
        st.markdown(f"**Relevance Score:** {source['similarity']:.4f}")
        st.markdown("**Excerpt:**")
        st.text(source.get('excerpt', 'No excerpt available'))

