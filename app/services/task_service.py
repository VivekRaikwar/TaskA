from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import logging
import structlog
from sqlalchemy.orm import Session
from ..models.database import Task, BatchJob
from ..schemas import TaskType, TaskStatus
from .ultrasafe_client import ultrasafe_client
from .cache_service import cache_service
from .rag_service import rag_service
from .webhook_service import webhook_service
from ..core.config import settings

logger = structlog.get_logger()

class TaskService:
    def __init__(self):
        self.task_handlers = {
            "classification": self._handle_classification,
            "entity_extraction": self._handle_entity_extraction,
            "summarization": self._handle_summarization,
            "sentiment_analysis": self._handle_sentiment_analysis
        }

    def _generate_input_hash(self, text: str) -> str:
        """Generate SHA-256 hash for input text."""
        return hashlib.sha256(text.encode()).hexdigest()

    async def create_task(
        self,
        db: Session,
        task_type: str,
        input_text: str,
        parameters: Dict[str, Any]
    ) -> Task:
        """Create a new NLP task."""
        # Check cache
        input_hash = self._generate_input_hash(input_text)
        cache_key = f"{task_type}:{input_hash}"
        
        if settings.CACHE_ENABLED:
            cached_result = cache_service.get(cache_key)
            if cached_result:
                logger.info("cache_hit", task_type=task_type, input_hash=input_hash)
                return cached_result

        # Create task
        task = Task(
            task_type=task_type,
            input_text=input_text,
            input_hash=input_hash,
            status=TaskStatus.PENDING
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Process task asynchronously
        await self._process_task(db, task.id)
        
        return task

    async def _process_task(self, db: Session, task_id: str):
        """Process a task asynchronously."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error("task_not_found", task_id=task_id)
            return

        try:
            # Update status
            task.status = TaskStatus.PROCESSING
            db.commit()

            # Get context if RAG is enabled
            context = None
            if task.parameters.get("use_rag", False):
                context = await rag_service.get_relevant_context(
                    task.input_text,
                    task.parameters.get("context_length", 1000)
                )

            # Process task
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"Unknown task type: {task.task_type}")

            result = await handler(task.input_text, task.parameters, context)

            # Update task
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            task.processing_time = (task.completed_at - task.created_at).total_seconds()
            db.commit()

            # Cache result
            if settings.CACHE_ENABLED:
                cache_service.set(
                    f"{task.task_type}:{task.input_hash}",
                    task,
                    ttl=settings.CACHE_TTL
                )

            # Send webhook notification
            if task.batch_job and task.batch_job.webhook_url:
                await webhook_service.send_notification(
                    db=db,
                    webhook_id=task.batch_job.webhook_url,
                    payload={
                        "event": "task.completed",
                        "task_id": task.id,
                        "result": result
                    }
                )

        except Exception as e:
            logger.error("task_failed", task_id=task_id, error=str(e))
            task.status = TaskStatus.FAILED
            task.error = str(e)
            db.commit()

            # Send webhook notification
            if task.batch_job and task.batch_job.webhook_url:
                await webhook_service.send_notification(
                    db=db,
                    webhook_id=task.batch_job.webhook_url,
                    payload={
                        "event": "task.failed",
                        "task_id": task.id,
                        "error": str(e)
                    }
                )

    async def _handle_classification(
        self,
        text: str,
        parameters: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle text classification task."""
        return await ultrasafe_client.classify_text(
            text=text,
            categories=parameters["categories"],
            context=context
        )

    async def _handle_entity_extraction(
        self,
        text: str,
        parameters: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle entity extraction task."""
        return await ultrasafe_client.extract_entities(
            text=text,
            entity_types=parameters["entity_types"],
            context=context
        )

    async def _handle_summarization(
        self,
        text: str,
        parameters: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle text summarization task."""
        return await ultrasafe_client.summarize_text(
            text=text,
            max_length=parameters["max_length"],
            context=context
        )

    async def _handle_sentiment_analysis(
        self,
        text: str,
        parameters: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle sentiment analysis task."""
        return await ultrasafe_client.analyze_sentiment(
            text=text,
            context=context
        )

    def get_task(self, db: Session, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return db.query(Task).filter(Task.id == task_id).first()

    async def create_batch_job(
        self,
        db: Session,
        tasks: List[Dict[str, Any]],
        webhook_url: Optional[str] = None
    ) -> BatchJob:
        """Create a batch job."""
        batch_job = BatchJob(
            status=TaskStatus.PENDING,
            total_tasks=len(tasks),
            webhook_url=webhook_url
        )
        db.add(batch_job)
        db.commit()
        db.refresh(batch_job)

        # Create tasks
        for task_data in tasks:
            task = Task(
                task_type=task_data["task_type"],
                input_text=task_data["text"],
                input_hash=self._generate_input_hash(task_data["text"]),
                status=TaskStatus.PENDING,
                batch_job_id=batch_job.id
            )
            db.add(task)

        db.commit()

        # Process batch job asynchronously
        await self._process_batch_job(db, batch_job.id)

        return batch_job

    async def _process_batch_job(self, db: Session, job_id: str):
        """Process a batch job asynchronously."""
        batch_job = db.query(BatchJob).filter(BatchJob.id == job_id).first()
        if not batch_job:
            logger.error("batch_job_not_found", job_id=job_id)
            return

        try:
            # Update status
            batch_job.status = TaskStatus.PROCESSING
            db.commit()

            # Process tasks
            tasks = db.query(Task).filter(Task.batch_job_id == job_id).all()
            results = {}

            for task in tasks:
                await self._process_task(db, task.id)
                task = self.get_task(db, task.id)
                
                if task.status == TaskStatus.COMPLETED:
                    batch_job.completed_tasks += 1
                    results[task.id] = task.result
                else:
                    batch_job.failed_tasks += 1
                    results[task.id] = {"error": task.error}

            # Update batch job
            batch_job.status = TaskStatus.COMPLETED
            batch_job.results = results
            batch_job.completed_at = datetime.utcnow()
            batch_job.processing_time = (batch_job.completed_at - batch_job.created_at).total_seconds()
            db.commit()

            # Send webhook notification
            if batch_job.webhook_url:
                await webhook_service.send_notification(
                    db=db,
                    webhook_id=batch_job.webhook_url,
                    payload={
                        "event": "batch_job.completed",
                        "job_id": batch_job.id,
                        "results": results
                    }
                )

        except Exception as e:
            logger.error("batch_job_failed", job_id=job_id, error=str(e))
            batch_job.status = TaskStatus.FAILED
            batch_job.error = str(e)
            db.commit()

            # Send webhook notification
            if batch_job.webhook_url:
                await webhook_service.send_notification(
                    db=db,
                    webhook_id=batch_job.webhook_url,
                    payload={
                        "event": "batch_job.failed",
                        "job_id": batch_job.id,
                        "error": str(e)
                    }
                )

    def get_batch_job(self, db: Session, job_id: str) -> Optional[BatchJob]:
        """Get batch job by ID."""
        return db.query(BatchJob).filter(BatchJob.id == job_id).first()

    def cancel_batch_job(self, db: Session, job_id: str) -> BatchJob:
        """Cancel a batch job."""
        batch_job = self.get_batch_job(db, job_id)
        if not batch_job:
            raise ValueError("Batch job not found")

        batch_job.status = TaskStatus.CANCELLED
        db.commit()

        # Cancel pending tasks
        tasks = db.query(Task).filter(
            Task.batch_job_id == job_id,
            Task.status == TaskStatus.PENDING
        ).all()

        for task in tasks:
            task.status = TaskStatus.CANCELLED
            db.commit()

        return batch_job

# Create singleton instance
task_service = TaskService() 