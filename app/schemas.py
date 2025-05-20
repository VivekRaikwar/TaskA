from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    CLASSIFICATION = "classification"
    ENTITY_EXTRACTION = "entity_extraction"
    SUMMARIZATION = "summarization"
    SENTIMENT_ANALYSIS = "sentiment_analysis"

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Request Models
class TextClassificationRequest(BaseModel):
    text: str = Field(..., min_length=1)
    categories: List[str] = Field(..., min_items=1)
    use_rag: bool = Field(default=False)
    context_length: int = Field(default=1000)

class EntityExtractionRequest(BaseModel):
    text: str = Field(..., min_length=1)
    entity_types: List[str] = Field(..., min_items=1)
    use_rag: bool = Field(default=False)
    context_length: int = Field(default=1000)

class SummarizationRequest(BaseModel):
    text: str = Field(..., min_length=1)
    max_length: int = Field(default=150)
    use_rag: bool = Field(default=False)
    context_length: int = Field(default=1000)

class SentimentAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1)
    use_rag: bool = Field(default=False)
    context_length: int = Field(default=1000)

class BatchTask(BaseModel):
    task_type: TaskType
    text: str = Field(..., min_length=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)

class BatchProcessingRequest(BaseModel):
    tasks: List[BatchTask] = Field(..., min_items=1)
    webhook_url: Optional[HttpUrl] = None

class WebhookCreateRequest(BaseModel):
    url: HttpUrl
    events: List[str] = Field(..., min_items=1)
    description: Optional[str] = None

# Response Models
class TaskResponse(BaseModel):
    id: str
    task_type: TaskType
    status: TaskStatus
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    processing_time: Optional[float]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

    class Config:
        from_attributes = True

class BatchJobStatus(BaseModel):
    id: str
    status: TaskStatus
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    processing_time: Optional[float]
    results: Optional[Dict[str, Any]]
    error: Optional[str]

    class Config:
        from_attributes = True

class WebhookResponse(BaseModel):
    id: str
    url: str
    events: List[str]
    description: Optional[str]
    is_active: bool
    failure_count: int
    last_triggered: Optional[datetime]
    last_status: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# NLP Result Models
class ClassificationResult(BaseModel):
    category: str
    confidence: float
    context: Optional[str] = None

class EntityResult(BaseModel):
    text: str
    type: str
    start: int
    end: int
    confidence: float
    context: Optional[str] = None

class SummarizationResult(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    context: Optional[str] = None

class SentimentResult(BaseModel):
    sentiment: str
    score: float
    confidence: float
    context: Optional[str] = None 