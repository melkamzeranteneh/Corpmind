from typing import List, TypedDict, Annotated
import operator

class GraphState(TypedDict):
    question: str
    expanded_queries: List[str]
    documents: List[dict]  # List of dicts with content and metadata
    relevance_scores: List[float]
    reranked_documents: List[dict]
    answer: str
    iterations: int
    is_relevant: bool
