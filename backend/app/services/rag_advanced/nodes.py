import json
from typing import List, Dict
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from app.db.utils import get_vector_store, get_graph_store
from app.core.config import settings
from .state import GraphState

class AdvancedNodes:
    def __init__(self):
        self.llm = ChatMistralAI(api_key=settings.MISTRAL_API_KEY, model="mistral-large-latest")
        self.vector_store = get_vector_store()
        self.graph_store = get_graph_store()

    def expand_query(self, state: GraphState):
        """Expand query into multiple variations."""
        print("---EXPANDING QUERY---")
        prompt = ChatPromptTemplate.from_template("""
        You are an AI assistant tasked with optimizing search queries.
        Generate 3 different variations of the following user question to improve retrieval.
        Output only a JSON list of strings.
        
        Question: {question}
        """)
        chain = prompt | self.llm | JsonOutputParser()
        queries = chain.invoke({"question": state["question"]})
        return {"expanded_queries": queries, "iterations": state.get("iterations", 0) + 1}

    def retrieve(self, state: GraphState):
        """Retrieve from both Vector and Graph databases."""
        print("---RETRIEVING---")
        queries = state["expanded_queries"] + [state["question"]]
        all_docs = []
        
        # 1. Vector Retrieval (Parallel for each query)
        for query in queries:
            docs = self.vector_store.similarity_search(query, k=2)
            all_docs.extend([{"content": d.page_content, "metadata": d.metadata} for d in docs])
        
        # 2. Graph Retrieval (Simple Cypher for entities)
        # This is a simplified version of GraphRAG
        graph_context = self.graph_store.query("""
        MATCH (n:__Entity__) 
        WHERE n.id IN $queries OR any(q IN $queries WHERE n.id CONTAINS q)
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN n.id as entity, type(r) as relationship, m.id as related_entity
        LIMIT 10
        """, params={"queries": queries})
        
        if graph_context:
            graph_text = "Graph Context:\n" + "\n".join([f"{r['entity']} {r['relationship']} {r['related_entity']}" for r in graph_context])
            all_docs.append({"content": graph_text, "metadata": {"source": "Neo4j"}})

        # Deduplicate by content
        seen = set()
        unique_docs = []
        for d in all_docs:
            if d["content"] not in seen:
                unique_docs.append(d)
                seen.add(d["content"])

        return {"documents": unique_docs}

    def grade_documents(self, state: GraphState):
        """Grade relevance of retrieved documents."""
        print("---GRADING DOCUMENTS---")
        prompt = ChatPromptTemplate.from_template("""
        You are a grader evaluating the relevance of a retrieved document to a user question.
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant.
        Output JSON with a single key 'relevance' and value 'yes' or 'no'.
        
        Question: {question}
        Document: {document}
        """)
        
        relevant_docs = []
        is_relevant = False
        
        # Just grade the first few or aggregate
        for doc in state["documents"][:5]:
            chain = prompt | self.llm | JsonOutputParser()
            result = chain.invoke({"question": state["question"], "document": doc["content"]})
            if result.get("relevance") == "yes":
                relevant_docs.append(doc)
                is_relevant = True
        
        return {"documents": relevant_docs if relevant_docs else state["documents"], "is_relevant": is_relevant}

    def rerank(self, state: GraphState):
        """Re-rank documents using a simple cross-encoder logic or LLM scoring."""
        print("---RERANKING---")
        # In a real app, we'd use BGE-Reranker. Here we use LLM for scoring for simplicity.
        prompt = ChatPromptTemplate.from_template("""
        Score the relevance of this document to the question from 0 to 10.
        Output only the number.
        
        Question: {question}
        Document: {document}
        """)
        
        scored_docs = []
        for doc in state["documents"]:
            chain = prompt | self.llm | StrOutputParser()
            try:
                score = float(chain.invoke({"question": state["question"], "document": doc["content"]}))
            except:
                score = 0.0
            scored_docs.append((score, doc))
        
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return {"reranked_documents": [d[1] for d in scored_docs[:5]]}

    def generate(self, state: GraphState):
        """Generate final answer."""
        print("---GENERATING---")
        prompt = ChatPromptTemplate.from_template("""
        You are a highly capable corporate AI assistant. Use the following context to provide a detailed, accurate answer.
        The context includes both text snippets and graph relationships.
        
        Context: {context}
        
        Question: {question}
        
        Answer:
        """)
        
        context = "\n\n".join([d["content"] for d in state["reranked_documents"]])
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": state["question"]})
        
        return {"answer": response}
