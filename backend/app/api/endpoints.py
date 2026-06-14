from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.rag_basic import BasicRAGService
from app.services.rag_advanced.graph import AdvancedRAGService
from app.ingestion.ingestor import Ingestor
from app.core.config import settings
from app.evaluation.pipeline import EvaluationPipeline

router = APIRouter()
ingestor = Ingestor()
basic_rag = BasicRAGService()
advanced_rag = AdvancedRAGService()
eval_pipeline = EvaluationPipeline()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    chunks: List[str]

class IngestRequest(BaseModel):
    directory: str = "data"
    mode: str = "advanced"  # basic or advanced

@router.post("/ingest")
async def ingest_data(request: IngestRequest):
    try:
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
        result = basic_rag.answer(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/advanced", response_model=QueryResponse)
async def query_advanced(request: QueryRequest):
    try:
        result = advanced_rag.answer(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluate")
async def run_eval():
    try:
        results = await eval_pipeline.run_evaluation()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
