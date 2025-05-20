from typing import List, Dict, Any, Optional
import pinecone
from sentence_transformers import SentenceTransformer
import numpy as np
import logging
import structlog
from ..core.config import settings

logger = structlog.get_logger()

class RAGService:
    def __init__(self):
        # Initialize Pinecone
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        
        # Get or create index
        if settings.RAG_INDEX_NAME not in pinecone.list_indexes():
            pinecone.create_index(
                name=settings.RAG_INDEX_NAME,
                dimension=384,  # Dimension for all-MiniLM-L6-v2
                metric="cosine"
            )
        
        self.index = pinecone.Index(settings.RAG_INDEX_NAME)
        
        # Initialize sentence transformer
        self.model = SentenceTransformer(settings.RAG_EMBEDDING_MODEL)

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error("embedding_generation_error", error=str(e))
            raise

    async def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add document to vector store."""
        try:
            # Generate embedding
            embedding = self._generate_embedding(text)
            
            # Generate document ID
            doc_id = f"doc_{len(self.index.describe_index_stats()['total_vector_count']) + 1}"
            
            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata["text"] = text
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(doc_id, embedding, doc_metadata)]
            )
            
            logger.info("document_added", doc_id=doc_id)
            return doc_id
            
        except Exception as e:
            logger.error("document_add_error", error=str(e))
            raise

    async def search_similar(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k or settings.RAG_TOP_K,
                include_metadata=True
            )
            
            # Format results
            matches = []
            for match in results.matches:
                if match.score >= settings.RAG_SCORE_THRESHOLD:
                    matches.append({
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata
                    })
            
            return matches
            
        except Exception as e:
            logger.error("similar_search_error", error=str(e))
            raise

    async def get_relevant_context(
        self,
        query: str,
        max_length: int = 1000
    ) -> Optional[str]:
        """Get relevant context for query."""
        try:
            # Search for similar documents
            matches = await self.search_similar(query)
            
            if not matches:
                return None
            
            # Combine text from matches
            context = []
            current_length = 0
            
            for match in matches:
                text = match["metadata"]["text"]
                if current_length + len(text) > max_length:
                    break
                context.append(text)
                current_length += len(text)
            
            return "\n".join(context)
            
        except Exception as e:
            logger.error("context_retrieval_error", error=str(e))
            return None

    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from vector store."""
        try:
            self.index.delete(ids=[doc_id])
            logger.info("document_deleted", doc_id=doc_id)
            return True
        except Exception as e:
            logger.error("document_delete_error", doc_id=doc_id, error=str(e))
            return False

# Create singleton instance
rag_service = RAGService() 