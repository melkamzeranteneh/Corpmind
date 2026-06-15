from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.rag_basic import BasicRAGService
from app.services.rag_advanced.graph import AdvancedRAGService
from app.ingestion.ingestor import Ingestor
from app.core.config import settings
from app.evaluation.pipeline import EvaluationPipeline

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    chunks: List[str]

class IngestRequest(BaseModel):
    directory: str = "data"
    mode: str = "advanced"  # basic or advanced

# Lazy initializers
_ingestor = None
_basic_rag = None
_advanced_rag = None
_eval_pipeline = None

def get_ingestor():
    global _ingestor
    if _ingestor is None:
        _ingestor = Ingestor()
    return _ingestor

def get_basic_rag():
    global _basic_rag
    if _basic_rag is None:
        _basic_rag = BasicRAGService()
    return _basic_rag

def get_advanced_rag():
    global _advanced_rag
    if _advanced_rag is None:
        _advanced_rag = AdvancedRAGService()
    return _advanced_rag

def get_eval_pipeline():
    global _eval_pipeline
    if _eval_pipeline is None:
        _eval_pipeline = EvaluationPipeline()
    return _eval_pipeline

@router.post("/ingest")
async def ingest_data(request: IngestRequest):
    try:
        ingestor = get_ingestor()
        if request.mode == "basic":
            ingestor.run_basic_ingestion(request.directory)
        else:
            ingestor.run_advanced_ingestion(request.directory)
        return {"message": f"{request.mode.capitalize()} ingestion successful."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/basic", response_model=QueryResponse)
async def query_basic(request: QueryRequest):
    try:
        basic_rag = get_basic_rag()
        result = basic_rag.answer(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/advanced", response_model=QueryResponse)
async def query_advanced(request: QueryRequest):
    try:
        advanced_rag = get_advanced_rag()
        result = advanced_rag.answer(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluate")
async def run_eval():
    try:
        eval_pipeline = get_eval_pipeline()
        results = await eval_pipeline.run_evaluation()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
