from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

# Request schemas
class TextClassificationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    categories: Optional[List[str]] = None
    use_rag: bool = False

class EntityExtractionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    entity_types: Optional[List[str]] = None
    use_rag: bool = False

class SummarizationRequest(BaseModel):
    text: str = Field(..., min_length=50)
    max_length: int = Field(100, ge=20, le=500)
    use_rag: bool = False

class SentimentAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    use_rag: bool = False

class BatchProcessingRequest(BaseModel):
    job_name: Optional[str] = None
    tasks: List[Dict[str, Any]]
    task_type: str  # 'classify', 'extract', 'summarize', 'sentiment'
    webhook_url: Optional[HttpUrl] = None

# Response schemas
class TaskResult(BaseModel):
    task_id: UUID
    task_type: str
    status: str
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime

class BatchJobStatus(BaseModel):
    job_id: UUID
    job_name: Optional[str]
    status: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    progress_percentage: float
    created_at: datetime
    completed_at: Optional[datetime] = None

class WebhookRequest(BaseModel):
    url: HttpUrl
    events: List[str] = Field(default=["task.completed", "batch.completed"])
    secret: Optional[str] = None

class WebhookResponse(BaseModel):
    webhook_id: UUID
    url: str
    events: List[str]
    active: bool
    created_at: datetime 