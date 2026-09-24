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
    
    def evaluate_retrieval(self) -> Dict:
        """
        Evaluate retrieval hit-rate.
        
        A 'hit' means the expected source document appears in the top-k results.
        
        Returns:
            Evaluation results dictionary
        """
        print("\n" + "="*70)
        print("📊 RETRIEVAL EVALUATION")
        print("="*70)
        print(f"Questions: {len(self.questions)}")
        print(f"Top-K: {self.retriever.top_k}")
        print(f"Threshold: {self.retriever.threshold}")
        print(f"Target hit-rate: {self.target_hit_rate:.0%}")
        
        hits = 0
        misses = 0
        results = []
        
        for i, q in enumerate(self.questions, 1):
            question = q['question']
            expected = q['expected_source']
            category = q.get('category', 'general')
            
            # Search
            retrieval = self.retriever.search(question)
            
            # Check if expected source is in results
            retrieved_sources = [r['source_file'] for r in retrieval['results']]
            is_hit = expected in retrieved_sources
            
            # Find rank of expected source
            rank = None
            for r in retrieval['results']:
                if r['source_file'] == expected:
                    rank = r['rank']
                    break
            
            if is_hit:
                hits += 1
                status = "✅ HIT"
            else:
                misses += 1
                status = "❌ MISS"
            
            print(f"\n[{i:2d}/{len(self.questions)}] {status} | Cat: {category}")
            print(f"   Q: {question}")
            print(f"   Expected: {expected}")
            
            if is_hit:
                print(f"   Found at rank: {rank} | Score: {retrieval['top_similarity']:.4f}")
            else:
                print(f"   Retrieved: {retrieved_sources[:3]}")
                print(f"   Top score: {retrieval['top_similarity']:.4f}")
            
            results.append({
                'id': q['id'],
                'question': question,
                'expected_source': expected,
                'category': category,
                'is_hit': is_hit,
                'rank': rank,
                'top_similarity': retrieval['top_similarity'],
                'retrieved_sources': retrieved_sources,
                'has_relevant_info': retrieval['has_relevant_info']
            })
        
        hit_rate = hits / len(self.questions) if self.questions else 0
        passed = hit_rate >= self.target_hit_rate
        
        print(f"\n{'='*70}")
        print(f"📈 RETRIEVAL RESULTS")
        print(f"   Hits: {hits}/{len(self.questions)}")
        print(f"   Misses: {misses}/{len(self.questions)}")
        print(f"   Hit Rate: {hit_rate:.2%}")
        print(f"   Target: {self.target_hit_rate:.0%}")
        print(f"   Status: {'✅ PASSED' if passed else '❌ NEEDS IMPROVEMENT'}")
        
        # Per-category breakdown
        categories = {}
        for r in results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = {'hits': 0, 'total': 0}
            categories[cat]['total'] += 1
            if r['is_hit']:
                categories[cat]['hits'] += 1
        
        if len(categories) > 1:
            print(f"\n📂 Per-Category Breakdown:")
            for cat, stats in categories.items():
                rate = stats['hits'] / stats['total']
                print(f"   {cat}: {stats['hits']}/{stats['total']} ({rate:.0%})")
        
        return {
            'hit_rate': hit_rate,
            'hits': hits,
            'misses': misses,
            'total': len(self.questions),
            'passed': passed,
            'target': self.target_hit_rate,
            'category_breakdown': categories,
            'detailed_results': results
        }
    
    def evaluate_refusal(self) -> Dict:
        """
        Test that the system refuses to answer out-of-scope questions.
        
        Returns:
            Refusal evaluation results
        """
        print("\n" + "="*70)
        print("🚫 REFUSAL EVALUATION (Hallucination Check)")
        print("="*70)
        
        refusals = 0
        hallucinations = 0
        results = []
        
        for i, question in enumerate(self.out_of_scope, 1):
            retrieval = self.retriever.search(question)
            
            # Check if below threshold (should refuse)
            should_refuse = not retrieval['has_relevant_info']
            did_refuse = retrieval['top_similarity'] < self.retriever.threshold
            
            if self.llm_available:
                # Full test with LLM
                answer_result = self.generator.answer(question)
                answer_text = answer_result['answer']
                is_refusal = "don't have enough information" in answer_text.lower()
            else:
                # Retrieval-only test
                answer_text = "N/A (LLM not available)"
                is_refusal = did_refuse
            
            if is_refusal:
                refusals += 1
                status = "✅ REFUSED"
            else:
                hallucinations += 1
                status = "⚠️ HALLUCINATION RISK"
            
            print(f"\n[{i}/{len(self.out_of_scope)}] {status}")
            print(f"   Q: {question}")
            print(f"   Top similarity: {retrieval['top_similarity']:.4f} (threshold: {self.retriever.threshold})")
            print(f"   Answer: {answer_text[:200]}...")
            
            results.append({
                'question': question,
                'top_similarity': retrieval['top_similarity'],
                'below_threshold': did_refuse,
                'is_refusal': is_refusal,
                'answer_preview': answer_text[:200]
            })
        
        refusal_rate = refusals / len(self.out_of_scope) if self.out_of_scope else 0
        
        print(f"\n{'='*70}")
        print(f"📈 REFUSAL RESULTS")
        print(f"   Refusals: {refusals}/{len(self.out_of_scope)}")
        print(f"   Hallucinations: {hallucinations}/{len(self.out_of_scope)}")
        print(f"   Refusal Rate: {refusal_rate:.2%}")
        print(f"   Status: {'✅ GOOD' if refusal_rate >= 0.8 else '⚠️ NEEDS IMPROVEMENT'}")
        
        return {
            'refusal_rate': refusal_rate,
            'refusals': refusals,
            'hallucinations': hallucinations,
            'total': len(self.out_of_scope),
            'passed': refusal_rate >= 0.8,
            'detailed_results': results
        }
    
    def evaluate_answer_quality(self) -> Dict:
        """
        Evaluate answer quality for in-scope questions.
        Requires LLM to be available.
        """
        if not self.llm_available:
            print("\n⚠️ LLM not available. Skipping answer quality evaluation.")
            return {'skipped': True, 'reason': 'LLM not available'}
        
        print("\n" + "="*70)
        print("📝 ANSWER QUALITY EVALUATION")
        print("="*70)
        
        results = []
        has_citation_count = 0
        refused_when_should_answer = 0
        
        sample_questions = self.questions[:10]  # Test first 10
        
        for i, q in enumerate(sample_questions, 1):
            question = q['question']
            expected = q['expected_source']
            
            result = self.generator.answer(question)
            answer = result['answer']
            
            # Check if answer has citations
            has_citation = "[Source:" in answer or "[source:" in answer.lower()
            
            # Check if it incorrectly refused
            is_refusal = "don't have enough information" in answer.lower()
            
            if has_citation:
                has_citation_count += 1
            
            if is_refusal:
                refused_when_should_answer += 1
            
            print(f"\n[{i}/{len(sample_questions)}]")
            print(f"   Q: {question}")
            print(f"   Has citations: {'✅' if has_citation else '❌'}")
            print(f"   Refused: {'⚠️' if is_refusal else '✅'}")
            print(f"   Answer preview: {answer[:200]}...")
            
            results.append({
                'question': question,
                'expected_source': expected,
                'has_citation': has_citation,
                'is_refusal': is_refusal,
                'answer_length': len(answer),
                'sources_count': len(result.get('sources', []))
            })
        
        citation_rate = has_citation_count / len(sample_questions) if sample_questions else 0
        
        print(f"\n📈 ANSWER QUALITY RESULTS")
        print(f"   Citation rate: {has_citation_count}/{len(sample_questions)} ({citation_rate:.0%})")
        print(f"   Incorrect refusals: {refused_when_should_answer}/{len(sample_questions)}")
        
        return {
            'citation_rate': citation_rate,
            'has_citation_count': has_citation_count,
            'incorrect_refusals': refused_when_should_answer,
            'total_tested': len(sample_questions),
            'detailed_results': results
        }
    
    