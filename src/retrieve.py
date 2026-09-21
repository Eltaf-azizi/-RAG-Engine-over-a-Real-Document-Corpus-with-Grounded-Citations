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
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize retriever with model and vector store connection."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load embedding model
        embed_config = self.config['embedding']
        self.model = SentenceTransformer(embed_config['model_name'])
        
        # Connect to ChromaDB
        vs_config = self.config['vector_store']
        self.client = chromadb.PersistentClient(path=vs_config['persist_directory'])
        
        try:
            self.collection = self.client.get_collection(vs_config['collection_name'])
            logger.info(f"Connected to collection: {vs_config['collection_name']} ({self.collection.count()} chunks)")
        except Exception as e:
            logger.error(f"Collection not found. Run embed_store.py first. Error: {e}")
            raise
        
        # Retrieval settings
        ret_config = self.config['retrieval']
        self.top_k = ret_config['top_k']
        self.threshold = ret_config['similarity_threshold']
    
    def search(self, query: str, top_k: Optional[int] = None) -> Dict:
        """
        Search for relevant document chunks.
        
        Args:
            query: User question
            top_k: Number of results (overrides config if provided)
            
        Returns:
            Dictionary with search results and metadata
        """
        if top_k is None:
            top_k = self.top_k
        
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        retrieved = []
        for i in range(len(results['documents'][0])):
            distance = results['distances'][0][i]
            similarity = 1 - distance  # Cosine distance to similarity
            
            retrieved.append({
                'rank': i + 1,
                'text': results['documents'][0][i],
                'source_file': results['metadatas'][0][i]['source_file'],
                'page': results['metadatas'][0][i]['page'],
                'similarity': round(similarity, 4),
                'distance': round(distance, 4)
            })
        
        # Determine if relevant information exists
        top_similarity = retrieved[0]['similarity'] if retrieved else 0.0
        has_relevant = top_similarity >= self.threshold
        
        return {
            'query': query,
            'has_relevant_info': has_relevant,
            'top_similarity': top_similarity,
            'threshold': self.threshold,
            'results_count': len(retrieved),
            'results': retrieved
        }

    
    def format_context(self, search_results: Dict) -> str:
        """
        Format search results into context string for LLM.
        
        Args:
            search_results: Output from search()
            
        Returns:
            Formatted context string
        """
        if not search_results['has_relevant_info']:
            return ""
        
        parts = []
        for r in search_results['results']:
            parts.append(
                f"[DOCUMENT {r['rank']}] "
                f"Source: {r['source_file']}, "
                f"Page: {r['page']}, "
                f"Relevance: {r['similarity']:.2%}\n"
                f"{r['text']}\n"
            )
        
        return "\n---\n".join(parts)
    
    def batch_search(self, queries: List[str]) -> List[Dict]:
        """Search multiple queries at once."""
        return [self.search(q) for q in queries]


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    retriever = Retriever()
    
    # Test queries
    test_queries = [
        {
            "query": "What fundamental rights do citizens have?",
            "expected": "Should find constitutional rights content"
        },
        {
            "query": "How is the president elected?",
            "expected": "Should find election procedure"
        },
        {
            "query": "How can the constitution be amended?",
            "expected": "Should find amendment process"
        },
        {
            "query": "What is the recipe for chocolate cake?",
            "expected": "Should have low similarity score"
        },
        {
            "query": "What provisions exist for emergency powers?",
            "expected": "Should find emergency provisions"
        }
    ]
    
    print("\n" + "="*70)
    print("RETRIEVAL TESTING")
    print("="*70)
    
    for test in test_queries:
        print(f"\n{'─'*70}")
        print(f"🔍 Query: {test['query']}")
        print(f"   Expected: {test['expected']}")
        
        result = retriever.search(test['query'])
        
        print(f"   Has relevant info: {'✅ YES' if result['has_relevant_info'] else '❌ NO'}")
        print(f"   Top similarity: {result['top_similarity']:.4f} (threshold: {result['threshold']})")
        print(f"\n   Top {min(2, len(result['results']))} results:")
        
        for r in result['results'][:2]:
            print(f"   #{r['rank']} [{r['similarity']:.4f}] {r['source_file']} - Page {r['page']}")
            print(f"      Preview: {r['text'][:150]}...")
    
    print("\n" + "="*70)
    print("✅ Retrieval testing complete")