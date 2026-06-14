import asyncio
from typing import List, Dict
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.rag_basic import BasicRAGService
from app.services.rag_advanced.graph import AdvancedRAGService
from app.core.config import settings

class EvaluationPipeline:
    def __init__(self):
        self.basic_rag = BasicRAGService()
        self.advanced_rag = AdvancedRAGService()
        self.llm = ChatMistralAI(api_key=settings.MISTRAL_API_KEY, model="mistral-large-latest")
        self.questions = [
            "What is the company policy on remote work for the engineering department?",
            "Tell me about the work-from-home rules for engineers.",
            "Which projects is John Doe working on, and who are his team members?",
            "What is the connection between Project Phoenix and the Marketing department?",
            "What is the company's policy on interstellar travel?",
            "Compare the benefits package for full-time employees versus contractors.",
            "Summarize the key objectives of the Q3 2024 roadmap.",
            "What is the architecture of the internal data warehouse as described in the docs?",
            "When was the last update to the security protocol?",
            "Who is the primary contact for HR-related queries in the London office?"
        ]

    async def compare_responses(self, question: str, basic_res: Dict, adv_res: Dict):
        prompt = ChatPromptTemplate.from_template("""
        You are an expert evaluator for RAG systems. Compare two answers provided by different RAG systems to the same question.
        
        Question: {question}
        
        System A (Basic RAG): {basic_answer}
        System B (Advanced RAG): {adv_answer}
        
        Evaluate based on:
        1. Accuracy (Is it factual?)
        2. Completeness (Does it cover all aspects?)
        3. Hallucination (Did it invent things?)
        
        Output JSON with keys: 'winner' (A, B, or Draw), 'reasoning', 'scores' (dict with A and B 0-10).
        """)
        chain = prompt | self.llm | JsonOutputParser()
        result = chain.invoke({
            "question": question,
            "basic_answer": basic_res["answer"],
            "adv_answer": adv_res["answer"]
        })
        return result

    async def run_evaluation(self):
        results = []
        for q in self.questions:
            print(f"Evaluating: {q}")
            basic_res = self.basic_rag.answer(q)
            adv_res = self.advanced_rag.answer(q)
            
            comparison = await self.compare_responses(q, basic_res, adv_res)
            
            results.append({
                "question": q,
                "basic": basic_res,
                "advanced": adv_res,
                "evaluation": comparison
            })
        return results
