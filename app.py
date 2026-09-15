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


def main():
    """Main Streamlit application."""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<p class="main-header">📜 Constitutional RAG Q&A</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub-header">Retrieval-Augmented Generation with Grounded Citations | '
            'Ask questions about constitutional documents</p>',
            unsafe_allow_html=True
        )
    with col2:
        st.metric("🕐", datetime.now().strftime("%H:%M"))
    
    st.divider()
    
    # Load generator
    generator = load_generator()
    
    if generator is None:
        st.stop()
    
    # Load config for sidebar
    config = load_config()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Configuration")
        
        st.metric("📏 Chunk Size", f"{config['ingestion']['chunk_size']} chars")
        st.metric("🔍 Top-K Results", config['retrieval']['top_k'])
        st.metric("🎯 Similarity Threshold", f"{config['retrieval']['similarity_threshold']}")
        
        st.divider()
        
        st.subheader("🤖 LLM Settings")
        st.metric("Provider", config['llm']['provider'].title())
        st.metric("Model", config['llm']['model'])
        st.metric("Temperature", config['llm']['temperature'])
        
        st.divider()
        
        st.subheader("📊 Collection Info")
        try:
            count = generator.retriever.collection.count()
            st.metric("Total Chunks", count)
        except:
            st.metric("Total Chunks", "N/A")
        
        st.divider()
        
        st.subheader("📖 Available Documents")
        try:
            # Get unique source files from collection
            results = generator.retriever.collection.get(include=['metadatas'])
            if results['metadatas']:
                sources = set(m['source_file'] for m in results['metadatas'])
                for source in sorted(sources):
                    st.markdown(f"• `{source}`")
        except:
            st.markdown("*Run ingestion first*")
        
        st.divider()
        
        st.subheader("❓ How It Works")
        st.markdown("""
        1. **Type a question** about any constitutional document
        2. **Retrieval**: System finds most relevant passages
        3. **Generation**: LLM creates answer using ONLY those passages
        4. **Citations**: Every fact includes source file and page number
        5. **Safety**: If nothing relevant is found, system refuses to answer
        """)
        
        st.divider()
        
        st.markdown("---")
        st.caption("Built with Sentence-Transformers, ChromaDB, and LLM")
        st.caption(f"v1.0.0 | © {datetime.now().year}")
    
    # Main content area
    st.markdown("### 🔍 Ask a Question")
    
    # Query input
    query = st.text_input(
        "Enter your question about the constitutional documents:",
        placeholder="e.g., What fundamental rights are guaranteed? How is the president elected? What is the amendment process?",
        key="query_input"
    )

    
    # Example questions
    with st.expander("💡 Example Questions"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Rights & Freedoms:**")
            st.markdown("- What fundamental rights do citizens have?")
            st.markdown("- How is freedom of speech protected?")
            st.markdown("- What rights do minorities have?")
            st.markdown("**Government Structure:**")
            st.markdown("- How is the president elected?")
            st.markdown("- What are the powers of the prime minister?")
        with col2:
            st.markdown("**Legal Processes:**")
            st.markdown("- How can the constitution be amended?")
            st.markdown("- What is the impeachment process?")
            st.markdown("- How are judges appointed?")
            st.markdown("**Powers & Limits:**")
            st.markdown("- What emergency powers exist?")
            st.markdown("- How is power divided between federal and state?")
    
    # Process query
    if query:
        with st.spinner("🔍 Searching documents and generating answer..."):
            result = generator.answer(query)
        
        st.divider()
        
        # Display answer
        st.markdown("### 📝 Answer")
        
        if not result['has_relevant_info']:
            st.markdown(
                f'<div class="refusal-box">'
                f'<strong>⚠️ Insufficient Information</strong><br>'
                f'{result["answer"]}<br><br>'
                f'<small>Top similarity score: {result["top_similarity"]:.4f} '
                f'(threshold: {result["threshold"]})</small>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            # Check if answer contains citations
            answer_text = result['answer']
            has_citations = '[Source:' in answer_text
            
            if has_citations:
                st.markdown(
                    f'<div class="success-box">{answer_text}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="warning-box">'
                    f'<strong>⚠️ Missing Citations</strong><br>'
                    f'{answer_text}</div>',
                    unsafe_allow_html=True
                )
            
            # Display sources
            if result['sources']:
                st.markdown("### 📚 Sources Used")
                
                for i, source in enumerate(result['sources'], 1):
                    display_source(source, i)
            
            # Metadata
            st.markdown("### 📊 Query Metadata")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Top Similarity", f"{result['top_similarity']:.4f}")
            with col2:
                st.metric("Threshold", f"{result['threshold']}")
            with col3:
                st.metric("Chunks Retrieved", result.get('retrieved_chunks', 'N/A'))
            with col4:
                st.metric("Model", result.get('model', 'N/A'))
    
    # Footer
    st.divider()
    st.markdown(
        '<p style="text-align: center; color: #6b7280;">'
        '⚠️ This system only answers based on provided constitutional documents. '
        'It will refuse to answer questions outside its knowledge base.'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()