from langchain_mistralai import ChatMistralAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.db.utils import get_vector_store
from app.core.config import settings

class BasicRAGService:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm = ChatMistralAI(api_key=settings.MISTRAL_API_KEY, model="mistral-large-latest")
        self.prompt = ChatPromptTemplate.from_template("""
        You are a helpful corporate assistant. Use the following context to answer the user's question.
        If you don't know the answer, just say that you don't know. Do not make up information.
        
        Context: {context}
        
        Question: {question}
        
        Answer:
        """)

    def answer(self, question: str):
        # 1. Retrieve
        docs = self.vector_store.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 2. Generate
        chain = self.prompt | self.llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": question})
        
        return {
            "answer": response,
            "sources": [doc.metadata.get("source") for doc in docs],
            "chunks": [doc.page_content for doc in docs]
        }
