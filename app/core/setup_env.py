import os

# Project Info
os.environ["PROJECT_NAME"] = "NLP Pipeline API"
os.environ["VERSION"] = "1.0.0"
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "true"

# Security
os.environ["API_KEY"] = "test-api-key-123"
os.environ["SECRET_KEY"] = "test-secret-key-456"

# Database
os.environ["POSTGRES_SERVER"] = "localhost"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "postgres"
os.environ["POSTGRES_DB"] = "nlp_pipeline"
os.environ["POSTGRES_PORT"] = "5432"

# Redis
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_PASSWORD"] = ""
os.environ["REDIS_DB"] = "0"

# UltraSafe API
os.environ["ULTRASAFE_API_KEY"] = "test-ultrasafe-api-key"
os.environ["ULTRASAFE_API_URL"] = "https://api.ultrasafe.ai/v1"

# Pinecone
os.environ["PINECONE_API_KEY"] = "test-pinecone-api-key"
os.environ["PINECONE_ENVIRONMENT"] = "test-environment"

# RAG Settings
os.environ["RAG_ENABLED"] = "true"
os.environ["RAG_INDEX_NAME"] = "nlp_pipeline"
os.environ["RAG_EMBEDDING_MODEL"] = "all-MiniLM-L6-v2"
os.environ["RAG_TOP_K"] = "3"
os.environ["RAG_SCORE_THRESHOLD"] = "0.7"

# Cache Settings
os.environ["CACHE_TTL"] = "3600"
os.environ["CACHE_ENABLED"] = "true"
os.environ["CACHE_PREFIX"] = "nlp_pipeline"

# Webhook Settings
os.environ["MAX_WEBHOOK_FAILURES"] = "3"
os.environ["WEBHOOK_TIMEOUT"] = "10"
os.environ["WEBHOOK_MAX_RETRIES"] = "3"
os.environ["WEBHOOK_RETRY_DELAY"] = "5"

# Logging
os.environ["LOG_LEVEL"] = "INFO" 