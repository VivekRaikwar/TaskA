from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    task_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    input_text = Column(Text, nullable=False)
    input_hash = Column(String, nullable=False)
    result = Column(JSON)
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    processing_time = Column(Float)  # in seconds
    batch_job_id = Column(String, ForeignKey("batch_jobs.id"), nullable=True)

    # Relationships
    batch_job = relationship("BatchJob", back_populates="tasks")

    def __repr__(self):
        return f"<Task {self.id} ({self.task_type})>"

class BatchJob(Base):
    __tablename__ = "batch_jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    status = Column(String, nullable=False, default="pending")
    total_tasks = Column(Integer, nullable=False)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    results = Column(JSON)
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    processing_time = Column(Float)  # in seconds

    # Relationships
    tasks = relationship("Task", back_populates="batch_job")

    def __repr__(self):
        return f"<BatchJob {self.id}>"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    content = Column(Text, nullable=False)
    metadata = Column(JSON)
    embedding_id = Column(String)  # ID in vector store
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Document {self.id}>"

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    url = Column(String, nullable=False)
    events = Column(JSON, nullable=False)  # List of event types to trigger webhook
    description = Column(Text)
    secret = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    failure_count = Column(Integer, default=0)
    last_triggered = Column(DateTime(timezone=True))
    last_status = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Webhook {self.id}>" 