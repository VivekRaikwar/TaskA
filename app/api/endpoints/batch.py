from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...schemas import (
    BatchProcessingRequest,
    BatchJobStatus,
    TaskResponse
)
from ..dependencies import (
    verify_api_key_dependency,
    get_db_session,
    get_task_service
)
from ...services.task_service import TaskService

router = APIRouter()

@router.post("/submit", response_model=BatchJobStatus)
async def submit_batch_job(
    request: BatchProcessingRequest,
    db: Session = Depends(get_db_session),
    task_service: TaskService = Depends(get_task_service),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Submit a batch job for processing."""
    if not request.tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tasks provided"
        )
    
    batch_job = await task_service.create_batch_job(
        db=db,
        tasks=request.tasks,
        webhook_url=str(request.webhook_url) if request.webhook_url else None
    )
    return batch_job

@router.get("/{job_id}/status", response_model=BatchJobStatus)
async def get_batch_job_status(
    job_id: str,
    db: Session = Depends(get_db_session),
    task_service: TaskService = Depends(get_task_service),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Get batch job status."""
    batch_job = task_service.get_batch_job(db, job_id)
    if not batch_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch job not found"
        )
    return batch_job

@router.get("/{job_id}/results", response_model=BatchJobStatus)
async def get_batch_job_results(
    job_id: str,
    db: Session = Depends(get_db_session),
    task_service: TaskService = Depends(get_task_service),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Get batch job results."""
    batch_job = task_service.get_batch_job(db, job_id)
    if not batch_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch job not found"
        )
    
    if batch_job.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch job is still processing"
        )
    
    if batch_job.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch job failed: {batch_job.error}"
        )
    
    return batch_job

@router.delete("/{job_id}", response_model=BatchJobStatus)
async def cancel_batch_job(
    job_id: str,
    db: Session = Depends(get_db_session),
    task_service: TaskService = Depends(get_task_service),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Cancel a batch job."""
    batch_job = task_service.get_batch_job(db, job_id)
    if not batch_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch job not found"
        )
    
    if batch_job.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel batch job in {batch_job.status} status"
        )
    
    batch_job = task_service.cancel_batch_job(db, job_id)
    return batch_job 