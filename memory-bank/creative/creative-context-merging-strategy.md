# 🎨🎨🎨 ENTERING CREATIVE PHASE: CONTEXT MERGING STRATEGY DESIGN

## Component Description
**Context Merging Strategy for Advanced RAG System** - The algorithm and approach for intelligently combining, ranking, and selecting relevant context from multiple Knowledge Collections when users query across collections, ensuring optimal context quality while respecting LLM context window limits.

## Requirements & Constraints

### Functional Requirements:
- Merge search results from multiple Knowledge Collections
- Re-rank combined results for relevance optimization
- Handle different embedding models across collections
- Respect LLM context window limits (typically 4K-32K tokens)
- Maintain source attribution for merged context
- Support configurable merging strategies per query type
- Handle cases where collections have conflicting information

### Non-Functional Requirements:
- **Performance**: Context merging < 200ms additional latency
- **Quality**: Maintain or improve retrieval relevance vs single collection
- **Scalability**: Support merging from 10+ collections simultaneously
- **Flexibility**: Pluggable merging algorithms for different use cases
- **Transparency**: Clear traceability of context selection decisions

### Technical Constraints:
- Different embedding models may have different similarity score ranges
- Collections may have different document types and quality levels
- LLM context windows vary by model (GPT-4: 8K-32K, Claude: 100K+)
- Real-time requirements for chat interface
- Memory constraints for large result sets

## Context Merging Options Analysis

### Option 1: Simple Concatenation
**Description**: Concatenate top-K results from each collection in order, truncate to fit context window.

**Pros**:
- Extremely simple to implement
- Minimal computational overhead
- Preserves original ranking from each collection
- Fast execution time
- Easy to debug and understand

**Cons**:
- No intelligent re-ranking across collections
- May include redundant or low-quality context
- Poor utilization of context window space
- No handling of score normalization across different embedding models
- May miss important context due to arbitrary truncation

**Technical Fit**: Low - Too simplistic for quality requirements
**Complexity**: Very Low - Trivial implementation
**Quality**: Low - Poor context optimization

### Option 2: Reciprocal Rank Fusion (RRF)
**Description**: Use RRF algorithm to merge and re-rank results from multiple collections based on their ranks rather than raw similarity scores.

**Pros**:
- Score-agnostic (works with different embedding models)
- Well-established algorithm with proven effectiveness
- Handles different score ranges naturally
- Relatively simple to implement
- Good balance of quality and performance

**Cons**:
- Doesn't consider actual content similarity between chunks
- May not handle very different collection sizes well
- Limited customization for domain-specific needs
- Rank-based approach may miss nuanced similarity differences

**Technical Fit**: High - Good balance for multi-collection scenario
**Complexity**: Low - Well-documented algorithm
**Quality**: Medium-High - Proven effectiveness in IR

### Option 3: LLM-Based Context Selection
**Description**: Use a smaller, fast LLM to evaluate and select the most relevant chunks from the combined result set.

**Pros**:
- Intelligent content-aware selection
- Can handle semantic similarity and relevance
- Flexible criteria based on query context
- Can eliminate redundant information
- High-quality context selection

**Cons**:
- Significant latency overhead (additional LLM call)
- Higher computational cost
- Potential for LLM hallucination in selection
- Complex prompt engineering required
- May become bottleneck under high load

**Technical Fit**: Medium - High quality but performance concerns
**Complexity**: High - Complex prompt engineering and error handling
**Quality**: High - Intelligent semantic selection

### Option 4: Hybrid Scoring with Semantic Clustering
**Description**: Normalize scores across collections, apply semantic clustering to remove redundancy, then re-rank using hybrid scoring.

**Pros**:
- Addresses score normalization across different models
- Removes redundant content through clustering
- Sophisticated ranking combining multiple signals
- Optimizes context window utilization
- Handles diverse collection characteristics

**Cons**:
- High computational complexity
- Requires additional embedding calls for clustering
- Complex parameter tuning required
- Potential for over-optimization
- Difficult to debug and maintain

**Technical Fit**: Medium - Sophisticated but complex
**Complexity**: Very High - Multiple algorithms and parameters
**Quality**: High - Comprehensive optimization

## Recommended Approach: Enhanced Reciprocal Rank Fusion (Option 2 + Enhancements)

### Rationale:
Enhanced RRF provides the optimal balance of quality, performance, and maintainability for the Advanced RAG System:

1. **Performance**: Fast execution suitable for real-time chat interface
2. **Quality**: Proven effectiveness in information retrieval scenarios
3. **Robustness**: Handles different embedding models and score ranges
4. **Simplicity**: Maintainable and debuggable implementation
5. **Extensibility**: Can be enhanced with additional signals over time

### Implementation Guidelines:

#### Core RRF Algorithm with Enhancements:

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

@dataclass
class SearchResult:
    chunk_id: str
    document_id: str
    collection_id: str
    similarity_score: float
    chunk_text: str
    metadata: Dict[str, Any]
    rank_in_collection: int

@dataclass
class MergedResult:
    chunk_id: str
    document_id: str
    collection_id: str
    original_score: float
    rrf_score: float
    final_score: float
    chunk_text: str
    metadata: Dict[str, Any]
    selection_reason: str

class EnhancedRRFMerger:
    def __init__(self, k: int = 60, collection_weights: Optional[Dict[str, float]] = None):
        """
        Enhanced RRF with collection weighting and quality signals
        
        Args:
            k: RRF parameter (typically 60)
            collection_weights: Optional weights per collection
        """
        self.k = k
        self.collection_weights = collection_weights or {}
    
    def merge_results(
        self,
        collection_results: Dict[str, List[SearchResult]],
        query: str,
        max_context_tokens: int = 4000,
        diversity_factor: float = 0.1
    ) -> List[MergedResult]:
        """
        Merge and re-rank results from multiple collections
        
        Args:
            collection_results: Results per collection
            query: Original user query for relevance assessment
            max_context_tokens: Maximum tokens for final context
            diversity_factor: Weight for diversity vs relevance
        """
        
        # Step 1: Apply base RRF scoring
        rrf_scores = self._calculate_rrf_scores(collection_results)
        
        # Step 2: Apply collection weights
        weighted_scores = self._apply_collection_weights(rrf_scores, collection_results)
        
        # Step 3: Apply quality signals
        quality_scores = self._apply_quality_signals(weighted_scores, collection_results)
        
        # Step 4: Apply diversity penalty
        final_scores = self._apply_diversity_penalty(quality_scores, diversity_factor)
        
        # Step 5: Select top results within token limit
        selected_results = self._select_within_token_limit(final_scores, max_context_tokens)
        
        return selected_results
    
    def _calculate_rrf_scores(self, collection_results: Dict[str, List[SearchResult]]) -> Dict[str, float]:
        """Calculate base RRF scores for all chunks"""
        rrf_scores = defaultdict(float)
        
        for collection_id, results in collection_results.items():
            for rank, result in enumerate(results, 1):
                # Standard RRF formula: 1 / (k + rank)
                rrf_score = 1.0 / (self.k + rank)
                rrf_scores[result.chunk_id] += rrf_score
        
        return dict(rrf_scores)
    
    def _apply_collection_weights(
        self, 
        rrf_scores: Dict[str, float], 
        collection_results: Dict[str, List[SearchResult]]
    ) -> Dict[str, float]:
        """Apply collection-specific weights to RRF scores"""
        weighted_scores = {}
        
        # Create chunk_id to collection mapping
        chunk_to_collection = {}
        for collection_id, results in collection_results.items():
            for result in results:
                chunk_to_collection[result.chunk_id] = collection_id
        
        for chunk_id, rrf_score in rrf_scores.items():
            collection_id = chunk_to_collection[chunk_id]
            weight = self.collection_weights.get(collection_id, 1.0)
            weighted_scores[chunk_id] = rrf_score * weight
        
        return weighted_scores
    
    def _apply_quality_signals(
        self,
        weighted_scores: Dict[str, float],
        collection_results: Dict[str, List[SearchResult]]
    ) -> Dict[str, float]:
        """Apply quality signals to improve ranking"""
        quality_scores = {}
        
        # Create chunk lookup
        chunk_lookup = {}
        for collection_id, results in collection_results.items():
            for result in results:
                chunk_lookup[result.chunk_id] = result
        
        for chunk_id, weighted_score in weighted_scores.items():
            result = chunk_lookup[chunk_id]
            
            # Quality signals
            quality_multiplier = 1.0
            
            # 1. Chunk size quality (prefer medium-sized chunks)
            chunk_length = len(result.chunk_text)
            if 200 <= chunk_length <= 1000:  # Optimal range
                quality_multiplier *= 1.1
            elif chunk_length < 100:  # Too short
                quality_multiplier *= 0.8
            elif chunk_length > 2000:  # Too long
                quality_multiplier *= 0.9
            
            # 2. Metadata quality signals
            if result.metadata.get('has_title', False):
                quality_multiplier *= 1.05
            
            if result.metadata.get('file_type') == 'PDF':
                quality_multiplier *= 1.02  # Slight preference for structured docs
            
            # 3. Recency signal (if available)
            created_at = result.metadata.get('created_at')
            if created_at:
                # Boost recent documents slightly
                days_old = (datetime.now() - created_at).days
                if days_old < 30:
                    quality_multiplier *= 1.03
            
            quality_scores[chunk_id] = weighted_score * quality_multiplier
        
        return quality_scores
    
    def _apply_diversity_penalty(
        self,
        quality_scores: Dict[str, float],
        diversity_factor: float
    ) -> Dict[str, float]:
        """Apply diversity penalty to reduce redundant content"""
        if diversity_factor == 0:
            return quality_scores
        
        # Sort by current scores
        sorted_chunks = sorted(quality_scores.items(), key=lambda x: x[1], reverse=True)
        
        final_scores = {}
        selected_texts = []
        
        for chunk_id, score in sorted_chunks:
            # Calculate similarity to already selected chunks
            chunk_text = self._get_chunk_text(chunk_id)
            
            max_similarity = 0.0
            for selected_text in selected_texts:
                similarity = self._calculate_text_similarity(chunk_text, selected_text)
                max_similarity = max(max_similarity, similarity)
            
            # Apply diversity penalty
            diversity_penalty = diversity_factor * max_similarity
            final_score = score * (1.0 - diversity_penalty)
            
            final_scores[chunk_id] = final_score
            selected_texts.append(chunk_text)
        
        return final_scores
    
    def _select_within_token_limit(
        self,
        final_scores: Dict[str, float],
        max_context_tokens: int
    ) -> List[MergedResult]:
        """Select top results within token limit"""
        # Sort by final scores
        sorted_chunks = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        selected_results = []
        total_tokens = 0
        
        for chunk_id, final_score in sorted_chunks:
            chunk_text = self._get_chunk_text(chunk_id)
            chunk_tokens = self._estimate_tokens(chunk_text)
            
            if total_tokens + chunk_tokens <= max_context_tokens:
                # Create merged result
                original_result = self._get_original_result(chunk_id)
                merged_result = MergedResult(
                    chunk_id=chunk_id,
                    document_id=original_result.document_id,
                    collection_id=original_result.collection_id,
                    original_score=original_result.similarity_score,
                    rrf_score=self._get_rrf_score(chunk_id),
                    final_score=final_score,
                    chunk_text=chunk_text,
                    metadata=original_result.metadata,
                    selection_reason=self._generate_selection_reason(original_result, final_score)
                )
                
                selected_results.append(merged_result)
                total_tokens += chunk_tokens
            else:
                break
        
        return selected_results
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity for diversity penalty"""
        # Simple Jaccard similarity for performance
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _generate_selection_reason(self, result: SearchResult, final_score: float) -> str:
        """Generate explanation for why this chunk was selected"""
        reasons = []
        
        if result.rank_in_collection <= 3:
            reasons.append(f"Top-{result.rank_in_collection} in {result.collection_id}")
        
        if final_score > 0.5:
            reasons.append("High relevance score")
        
        if len(result.chunk_text) >= 200:
            reasons.append("Substantial content")
        
        return "; ".join(reasons) if reasons else "Selected by RRF algorithm"
```

#### Advanced Context Optimization:

```python
class ContextOptimizer:
    def __init__(self):
        self.sentence_splitter = self._init_sentence_splitter()
    
    def optimize_context_order(self, merged_results: List[MergedResult], query: str) -> List[MergedResult]:
        """Optimize the order of context chunks for better LLM performance"""
        
        # Strategy: Place most relevant chunks first and last (primacy/recency effect)
        if len(merged_results) <= 2:
            return merged_results
        
        # Sort by relevance
        sorted_results = sorted(merged_results, key=lambda x: x.final_score, reverse=True)
        
        # Optimized ordering: High-Med-Low-Med-High pattern
        optimized_order = []
        
        # Add highest relevance first
        optimized_order.append(sorted_results[0])
        
        # Add medium relevance in middle
        mid_results = sorted_results[2:-1] if len(sorted_results) > 3 else []
        optimized_order.extend(mid_results)
        
        # Add second highest last (recency effect)
        if len(sorted_results) > 1:
            optimized_order.append(sorted_results[1])
        
        return optimized_order
    
    def create_context_summary(self, merged_results: List[MergedResult]) -> str:
        """Create a summary of the context for the LLM"""
        collections = set(r.collection_id for r in merged_results)
        doc_count = len(set(r.document_id for r in merged_results))
        
        summary = f"Context from {len(collections)} collections, {doc_count} documents:\n"
        
        for i, result in enumerate(merged_results, 1):
            summary += f"\n[{i}] From {result.collection_id}: {result.chunk_text[:100]}...\n"
        
        return summary
```

#### Query-Specific Merging Strategies:

```python
class QueryAwareMerger:
    def __init__(self):
        self.base_merger = EnhancedRRFMerger()
    
    def merge_with_query_analysis(
        self,
        collection_results: Dict[str, List[SearchResult]],
        query: str,
        query_type: str = "general"
    ) -> List[MergedResult]:
        """Apply query-specific merging strategies"""
        
        if query_type == "factual":
            # For factual queries, prefer recent, authoritative sources
            collection_weights = self._get_factual_weights(collection_results)
            merger = EnhancedRRFMerger(collection_weights=collection_weights)
            return merger.merge_results(collection_results, query, diversity_factor=0.05)
        
        elif query_type == "analytical":
            # For analytical queries, prefer diverse perspectives
            return self.base_merger.merge_results(collection_results, query, diversity_factor=0.2)
        
        elif query_type == "procedural":
            # For how-to queries, prefer step-by-step content
            return self._merge_procedural(collection_results, query)
        
        else:
            # Default general merging
            return self.base_merger.merge_results(collection_results, query)
    
    def _get_factual_weights(self, collection_results: Dict[str, List[SearchResult]]) -> Dict[str, float]:
        """Determine collection weights for factual queries"""
        weights = {}
        
        for collection_id in collection_results.keys():
            # Example: Weight based on collection metadata
            if "official" in collection_id.lower():
                weights[collection_id] = 1.3
            elif "wiki" in collection_id.lower():
                weights[collection_id] = 1.1
            else:
                weights[collection_id] = 1.0
        
        return weights
```

## Verification Checkpoint

### Requirements Coverage:
- ✅ **Multi-Collection Merging**: Enhanced RRF handles multiple collections effectively
- ✅ **Score Normalization**: RRF is score-agnostic, works across different embedding models
- ✅ **Context Window Management**: Token-aware selection within limits
- ✅ **Source Attribution**: Full traceability maintained through MergedResult objects
- ✅ **Performance**: Fast execution suitable for real-time requirements
- ✅ **Quality Optimization**: Multiple quality signals and diversity handling

### Technical Feasibility:
- ✅ **Algorithm Maturity**: RRF is well-established and proven
- ✅ **Implementation Complexity**: Manageable complexity with clear structure
- ✅ **Performance Characteristics**: O(n log n) complexity suitable for real-time use
- ✅ **Extensibility**: Pluggable architecture for additional signals

### Risk Assessment:
- **Low Risk**: RRF algorithm is well-understood and stable
- **Medium Risk**: Quality signals require tuning and validation
- **Low Risk**: Performance characteristics meet real-time requirements
- **Mitigation**: Comprehensive testing and gradual rollout of enhancements

### Implementation Readiness:
- ✅ Core RRF algorithm with enhancements specified
- ✅ Quality signals and diversity handling defined
- ✅ Context optimization strategies outlined
- ✅ Query-aware merging approaches documented
- ✅ Performance and token management addressed

# 🎨🎨🎨 EXITING CREATIVE PHASE: CONTEXT MERGING STRATEGY DESIGN

**Decision**: Enhanced Reciprocal Rank Fusion with quality signals, diversity penalty, and query-aware optimizations
**Next**: Proceed to Chat Interface UX Design creative phase 