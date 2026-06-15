import os
from langchain_mistralai import MistralAIEmbeddings
from langchain_chroma import Chroma
from langchain_neo4j import Neo4jGraph
from app.core.config import settings

def get_embeddings():
    return MistralAIEmbeddings(api_key=settings.MISTRAL_API_KEY)

def get_vector_store():
    return Chroma(
        persist_directory=settings.CHROMA_DB_PATH,
        embedding_function=get_embeddings(),
        collection_name="corporate_knowledge"
    )

def get_graph_store():
    return Neo4jGraph(
        url=settings.NEO4J_URI,
        username=settings.NEO4J_USERNAME,
        password=settings.NEO4J_PASSWORD
    )
