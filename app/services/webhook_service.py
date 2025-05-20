from typing import Dict, Any, Optional
import httpx
import logging
import structlog
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.database import Webhook
from ..core.config import settings

logger = structlog.get_logger()

class WebhookService:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.timeout = 10  # seconds

    async def send_notification(
        self,
        db: Session,
        webhook_id: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Send a webhook notification."""
        webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not webhook:
            logger.error("webhook_not_found", webhook_id=webhook_id)
            return False

        if not webhook.is_active:
            logger.warning("webhook_inactive", webhook_id=webhook_id)
            return False

        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"{settings.PROJECT_NAME}/1.0.0",
            "X-Webhook-ID": webhook_id,
            "X-Webhook-Signature": self._generate_signature(payload, webhook.secret)
        }

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        webhook.url,
                        json=payload,
                        headers=headers
                    )
                    response.raise_for_status()

                    # Update webhook status
                    webhook.last_triggered = datetime.utcnow()
                    webhook.last_status = response.status_code
                    webhook.failure_count = 0
                    db.commit()

                    logger.info(
                        "webhook_sent",
                        webhook_id=webhook_id,
                        status_code=response.status_code
                    )
                    return True

            except httpx.HTTPError as e:
                logger.error(
                    "webhook_http_error",
                    webhook_id=webhook_id,
                    error=str(e),
                    attempt=attempt + 1
                )
                webhook.failure_count += 1
                webhook.last_status = getattr(e.response, "status_code", None)
                db.commit()

                if webhook.failure_count >= settings.MAX_WEBHOOK_FAILURES:
                    webhook.is_active = False
                    db.commit()
                    logger.warning(
                        "webhook_deactivated",
                        webhook_id=webhook_id,
                        failure_count=webhook.failure_count
                    )
                    return False

            except Exception as e:
                logger.error(
                    "webhook_error",
                    webhook_id=webhook_id,
                    error=str(e),
                    attempt=attempt + 1
                )
                webhook.failure_count += 1
                db.commit()

            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay)

        return False

    def _generate_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        import hmac
        import hashlib
        import json

        message = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def validate_url(self, url: str) -> bool:
        """Validate webhook URL."""
        try:
            result = httpx.URL(url)
            return result.scheme in ("http", "https")
        except Exception:
            return False

    def create_webhook(
        self,
        db: Session,
        url: str,
        events: list,
        description: Optional[str] = None
    ) -> Webhook:
        """Create a new webhook."""
        if not self.validate_url(url):
            raise ValueError("Invalid webhook URL")

        webhook = Webhook(
            url=url,
            events=events,
            description=description,
            secret=self._generate_secret(),
            is_active=True
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        return webhook

    def _generate_secret(self) -> str:
        """Generate a random webhook secret."""
        import secrets
        return secrets.token_urlsafe(32)

# Create singleton instance
webhook_service = WebhookService() 