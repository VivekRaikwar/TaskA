from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import verify_api_key
from ..services.task_service import task_service
from ..services.cache_service import cache_service
from ..services.rag_service import rag_service
from ..services.ultrasafe_client import ultrasafe_client
from ..core.config import settings

# API key header
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key_dependency(api_key: str = Depends(api_key_header)):
    """Verify API key from header."""
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key

# Service dependencies
def get_task_service():
    """Get task service instance."""
    return task_service

def get_cache_service():
    """Get cache service instance."""
    return cache_service

def get_rag_service():
    """Get RAG service instance."""
    return rag_service

def get_ultrasafe_client():
    """Get UltraSafe client instance."""
    return ultrasafe_client

# Database dependency
def get_db_session() -> Generator[Session, None, None]:
    """Get database session."""
    return get_db() 