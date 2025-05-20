from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...schemas import (
    TextClassificationRequest,
    EntityExtractionRequest,
    SummarizationRequest,
    SentimentAnalysisRequest,
    TaskResponse,
    ClassificationResult,
    EntityResult,
    SummarizationResult,
    SentimentResult
)
from ..dependencies import (
    verify_api_key_dependency,
    get_db_session,
    get_task_service,
    get_cache_service,
    get_rag_service
)
from ...services.task_service import TaskService
from ...services.cache_service import CacheService
from ...services.rag_service import RAGService

router = APIRouter()

@router.post("/classify", response_model=TaskResponse)
async def classify_text(
    request: TextClassificationRequest,
    db: Session = Depends(get_db_session),
    task_service: TaskService = Depends(get_task_service),
    cache_service: CacheService = Depends(get_cache_service),
    rag_service: RAGService = Depends(get_rag_service),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Classify text into categories."""
    task = await task_service.create_task(
        db=db,
        task_type="classification",
        input_text=request.text,
        parameters={
            "categories": request.categories,
            "use_rag": request.use_rag,
            "context_length": request.context_length
        }
    )
    return task

@router.post("/extract-entities", response_model=TaskResponse)
async def extract_entities(
    request: EntityExtractionRequest,
    db: Session = Depends(get_db_session),
    task_service: TaskService = Depends(get_task_service),
    cache_service: CacheService = Depends(get_cache_service),
    rag_service: RAGService = Depends(get_rag_service),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Extract entities from text."""
    task = await task_service.create_task(
        db=db,
        task_type="entity_extraction",
        input_text=request.text,
        parameters={
            "entity_types": request.entity_types,
            "use_rag": request.use_rag,
            "context_length": request.context_length
        }
    )
    return task

@router.post("/summarize", response_model=TaskResponse)
async def summarize_text(
    request: SummarizationRequest,
    db: Session = Depends(get_db_session),
    task_service: TaskService = Depends(get_task_service),
    cache_service: CacheService = Depends(get_cache_service),
    rag_service: RAGService = Depends(get_rag_service),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Summarize text."""
    task = await task_service.create_task(
        db=db,
        task_type="summarization",
        input_text=request.text,
        parameters={
            "max_length": request.max_length,
            "use_rag": request.use_rag,
            "context_length": request.context_length
        }
    )
    return task

@router.post("/analyze-sentiment", response_model=TaskResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    db: Session = Depends(get_db_session),
    task_service: TaskService = Depends(get_task_service),
    cache_service: CacheService = Depends(get_cache_service),
    rag_service: RAGService = Depends(get_rag_service),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Analyze sentiment of text."""
    task = await task_service.create_task(
        db=db,
        task_type="sentiment_analysis",
        input_text=request.text,
        parameters={
            "use_rag": request.use_rag,
            "context_length": request.context_length
        }
    )
    return task

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    db: Session = Depends(get_db_session),
    task_service: TaskService = Depends(get_task_service),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Get task status and results."""
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task 