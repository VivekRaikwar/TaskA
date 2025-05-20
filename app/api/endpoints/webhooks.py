from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...schemas import (
    WebhookCreateRequest,
    WebhookResponse
)
from ..dependencies import (
    verify_api_key_dependency,
    get_db_session,
    get_task_service
)
from ...services.webhook_service import webhook_service
from ...services.task_service import TaskService

router = APIRouter()

@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    request: WebhookCreateRequest,
    db: Session = Depends(get_db_session),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Register a new webhook."""
    try:
        webhook = webhook_service.create_webhook(
            db=db,
            url=str(request.url),
            events=request.events,
            description=request.description
        )
        return webhook
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    db: Session = Depends(get_db_session),
    api_key: str = Depends(verify_api_key_dependency)
):
    """List all registered webhooks."""
    webhooks = webhook_service.list_webhooks(db)
    return webhooks

@router.delete("/{webhook_id}", response_model=WebhookResponse)
async def delete_webhook(
    webhook_id: str,
    db: Session = Depends(get_db_session),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Delete a webhook."""
    webhook = webhook_service.get_webhook(db, webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    webhook_service.delete_webhook(db, webhook_id)
    return webhook

@router.post("/{webhook_id}/test", response_model=WebhookResponse)
async def test_webhook(
    webhook_id: str,
    db: Session = Depends(get_db_session),
    api_key: str = Depends(verify_api_key_dependency)
):
    """Test a webhook by sending a test event."""
    webhook = webhook_service.get_webhook(db, webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    if not webhook.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook is not active"
        )
    
    success = await webhook_service.send_notification(
        db=db,
        webhook_id=webhook_id,
        payload={
            "event": "test",
            "timestamp": "2024-01-01T00:00:00Z",
            "data": {
                "message": "This is a test webhook event"
            }
        }
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test webhook"
        )
    
    return webhook 