from celery import Celery
from .core.config import settings
import logging
import structlog

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

# Create Celery app
celery_app = Celery(
    "nlp_pipeline",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="default",
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "nlp": {
            "exchange": "nlp",
            "routing_key": "nlp",
        },
    },
    task_routes={
        "app.tasks.process_nlp_task": {"queue": "nlp"},
        "app.tasks.process_batch_job": {"queue": "nlp"},
    }
)

# Create logger
logger = structlog.get_logger()

@celery_app.task(bind=True)
def process_nlp_task(self, task_id: str):
    """Process an NLP task asynchronously."""
    from .services.task_service import task_service
    from .core.database import SessionLocal
    
    logger.info("processing_nlp_task", task_id=task_id)
    
    try:
        db = SessionLocal()
        task_service._process_task(db, task_id)
        logger.info("nlp_task_completed", task_id=task_id)
    except Exception as e:
        logger.error("nlp_task_failed", task_id=task_id, error=str(e))
        raise
    finally:
        db.close()

@celery_app.task(bind=True)
def process_batch_job(self, job_id: str):
    """Process a batch job asynchronously."""
    from .services.task_service import task_service
    from .core.database import SessionLocal
    
    logger.info("processing_batch_job", job_id=job_id)
    
    try:
        db = SessionLocal()
        task_service._process_batch_job(db, job_id)
        logger.info("batch_job_completed", job_id=job_id)
    except Exception as e:
        logger.error("batch_job_failed", job_id=job_id, error=str(e))
        raise
    finally:
        db.close()

@celery_app.task(bind=True)
def send_webhook(self, webhook_id: str, payload: dict):
    """Send webhook notification asynchronously."""
    from .services.webhook_service import webhook_service
    from .core.database import SessionLocal
    
    logger.info("sending_webhook", webhook_id=webhook_id)
    
    try:
        db = SessionLocal()
        webhook_service.send_notification(db, webhook_id, payload)
        logger.info("webhook_sent", webhook_id=webhook_id)
    except Exception as e:
        logger.error("webhook_failed", webhook_id=webhook_id, error=str(e))
        raise
    finally:
        db.close()

if __name__ == "__main__":
    celery_app.start() 