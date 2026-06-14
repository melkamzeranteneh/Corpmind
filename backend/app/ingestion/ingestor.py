import os
from typing import List
from langchain_community.document_loaders import UnstructuredMarkdownLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_mistralai import ChatMistralAI
from app.db.utils import get_vector_store, get_graph_store
from app.core.config import settings

class Ingestor:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.graph_store = get_graph_store()
        self.llm = ChatMistralAI(api_key=settings.MISTRAL_API_KEY, model="mistral-large-latest")
        self.graph_transformer = LLMGraphTransformer(llm=self.llm)

    def load_documents(self, directory_path: str):
        loader = DirectoryLoader(directory_path, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
        return loader.load()

    def run_basic_ingestion(self, directory_path: str):
        """Fixed-size chunking and vector indexing."""
        docs = self.load_documents(directory_path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)
        self.vector_store.add_documents(chunks)
        print(f"Basic ingestion complete: {len(chunks)} chunks added to Chroma.")

    def run_advanced_ingestion(self, directory_path: str):
        """Parent-child chunking and Graph indexing."""
        docs = self.load_documents(directory_path)
        
        # 1. Graph Ingestion
        graph_documents = self.graph_transformer.convert_to_graph_documents(docs)
        self.graph_store.add_graph_documents(graph_documents, baseEntityLabel=True, include_source=True)
        
        # 2. Parent-Child Vector Ingestion
        # For simplicity in this demo, we'll store parent docs in Neo4j and child chunks in Chroma
        # and link them. Or just use a MultiVectorRetriever pattern.
        # Here we'll do standard Recursive splitting but with metadata linking.
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        
        all_child_chunks = []
        for doc in docs:
            parent_chunks = parent_splitter.split_documents([doc])
            for i, p_chunk in enumerate(parent_chunks):
                p_chunk.metadata["doc_id"] = f"{doc.metadata.get('source')}_p{i}"
                child_chunks = child_splitter.split_documents([p_chunk])
                for c_chunk in child_chunks:
                    c_chunk.metadata["parent_id"] = p_chunk.metadata["doc_id"]
                    all_child_chunks.append(c_chunk)
        
        self.vector_store.add_documents(all_child_chunks)
        print(f"Advanced ingestion complete: {len(all_child_chunks)} child chunks added to Chroma and graph updated.")
