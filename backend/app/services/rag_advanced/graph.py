from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes import AdvancedNodes

def create_advanced_rag_graph():
    nodes = AdvancedNodes()
    workflow = StateGraph(GraphState)

    # Add Nodes
    workflow.add_node("expand_query", nodes.expand_query)
    workflow.add_node("retrieve", nodes.retrieve)
    workflow.add_node("grade_documents", nodes.grade_documents)
    workflow.add_node("rerank", nodes.rerank)
    workflow.add_node("generate", nodes.generate)

    # Build Graph
    workflow.set_entry_point("expand_query")
    workflow.add_edge("expand_query", "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    # Conditional Edge for CRAG
    def decide_to_generate(state: GraphState):
        if state["is_relevant"] or state.get("iterations", 0) > 2:
            return "rerank"
        else:
            return "expand_query"

    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "rerank": "rerank",
            "expand_query": "expand_query"
        }
    )

    workflow.add_edge("rerank", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()

class AdvancedRAGService:
    def __init__(self):
        self.graph = create_advanced_rag_graph()

    def answer(self, question: str):
        initial_state = {
            "question": question,
            "expanded_queries": [],
            "documents": [],
            "reranked_documents": [],
            "iterations": 0,
            "is_relevant": False
        }
        result = self.graph.invoke(initial_state)
        return {
            "answer": result["answer"],
            "sources": [d["metadata"].get("source") for d in result["reranked_documents"]],
            "chunks": [d["content"] for d in result["reranked_documents"]]
        }
