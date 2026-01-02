"""
Qdrant Document Store

Manages vector storage and retrieval using Qdrant.
Integrates with Haystack 2.x for RAG pipelines.
"""

from typing import List, Optional, Dict, Any
import logging
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from haystack.dataclasses import Document
from src.config.settings import settings

logger = logging.getLogger(__name__)


class QdrantDocumentStore:
    """
    Qdrant-based document store for vector similarity search.
    
    Features:
    - Vector storage with metadata
    - Similarity search with filtering
    - Document CRUD operations
    - Collection management
    """
    
    def __init__(
        self,
        collection_name: Optional[str] = None,
        embedding_dimension: Optional[int] = None,
        distance_metric: Distance = Distance.COSINE,
    ):
        """
        Initialize Qdrant document store.
        
        Args:
            collection_name: Name of the Qdrant collection
            embedding_dimension: Dimension of embedding vectors
            distance_metric: Distance metric for similarity (COSINE, EUCLID, DOT)
        """
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.embedding_dimension = embedding_dimension or settings.embedding_dimension
        self.distance_metric = distance_metric
        
        # Initialize Qdrant client
        connection_params = settings.qdrant_connection
        if "url" in connection_params:
            # Cloud connection
            self.client = QdrantClient(
                url=connection_params["url"],
                api_key=connection_params.get("api_key"),
            )
            logger.info(f"Connected to Qdrant Cloud: {connection_params['url']}")
        else:
            # Local connection
            self.client = QdrantClient(
                host=connection_params["host"],
                port=connection_params["port"],
            )
            logger.info(
                f"Connected to Qdrant: {connection_params['host']}:{connection_params['port']}"
            )
        
        # Ensure collection exists
        self._ensure_collection()
    
    def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=self.distance_metric,
                    ),
                )
                logger.info(
                    f"Created collection '{self.collection_name}' "
                    f"(dim={self.embedding_dimension}, metric={self.distance_metric})"
                )
            else:
                logger.info(f"Using existing collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            raise
    
    def write_documents(
        self,
        documents: List[Document],
        batch_size: int = 100,
    ) -> int:
        """
        Write documents with embeddings to Qdrant.
        
        Args:
            documents: List of Haystack Document objects with embeddings
            batch_size: Number of documents to write per batch
            
        Returns:
            Number of documents written
        """
        if not documents:
            logger.warning("No documents to write")
            return 0
        
        points = []
        for doc in documents:
            if doc.embedding is None:
                logger.warning(f"Document {doc.id} has no embedding, skipping")
                continue
            
            # ID Scheme Version: v1 - UUID format from MD5 hash
            # Convert document ID to UUID string for Qdrant point ID
            # MD5 produces 128-bit hash which maps to UUID format
            # Store original ID in payload for lookups
            md5_hash = hashlib.md5(str(doc.id).encode()).hexdigest()
            point_id = f"{md5_hash[:8]}-{md5_hash[8:12]}-{md5_hash[12:16]}-{md5_hash[16:20]}-{md5_hash[20:]}"
            
            # Prepare metadata (exclude embedding from payload)
            payload = {
                "content": doc.content,
                "doc_id": str(doc.id),  # Original ID
                **doc.meta,
            }
            
            # Create Qdrant point
            point = PointStruct(
                id=point_id,
                vector=doc.embedding,
                payload=payload,
            )
            points.append(point)
        
        if not points:
            logger.warning("No valid points to write (all documents missing embeddings)")
            return 0
        
        # Write in batches
        total_written = 0
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )
                total_written += len(batch)
                logger.info(f"Wrote batch of {len(batch)} documents to Qdrant")
            except Exception as e:
                logger.error(f"Failed to write batch: {e}")
                raise
        
        logger.info(f"Successfully wrote {total_written} documents to Qdrant")
        return total_written
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
    ) -> List[Document]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filters: Metadata filters (e.g., {"document_id": "doc123"})
            score_threshold: Minimum similarity score
            
        Returns:
            List of matching Haystack Document objects with scores
        """
        # Build Qdrant filter
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )
            if conditions:
                qdrant_filter = Filter(must=conditions)
        
        # Search
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
                query_filter=qdrant_filter,
                score_threshold=score_threshold,
            ).points
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
        
        # Convert to Haystack Documents
        documents = []
        for result in results:
            doc = Document(
                id=result.payload.get("doc_id"),
                content=result.payload.get("content", ""),
                meta={
                    k: v
                    for k, v in result.payload.items()
                    if k not in ["content", "doc_id"]
                },
                score=result.score,
            )
            documents.append(doc)
        
        logger.info(f"Found {len(documents)} documents with similarity search")
        return documents
    
    def delete_documents(
        self,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Delete documents by IDs or filters.
        
        Args:
            document_ids: List of document IDs to delete
            filters: Metadata filters for deletion
            
        Returns:
            Number of documents deleted. For filter-based deletion, returns -1
            to indicate success but unknown count (Qdrant does not provide
            deletion counts for filter-based operations). Returns 0 if no
            parameters provided (no-op).
        """
        if document_ids:
            # ID Scheme Version: v1 - UUID format from MD5 hash
            # Convert document IDs to UUID strings matching write_documents format
            point_ids = []
            for doc_id in document_ids:
                md5_hash = hashlib.md5(str(doc_id).encode()).hexdigest()
                point_id = f"{md5_hash[:8]}-{md5_hash[8:12]}-{md5_hash[12:16]}-{md5_hash[16:20]}-{md5_hash[20:]}"
                point_ids.append(point_id)
            try:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids,
                )
                logger.info(f"Deleted {len(document_ids)} documents")
                return len(document_ids)
            except Exception as e:
                logger.error(f"Failed to delete documents: {e}")
                raise
        
        if filters:
            # Build filter
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )
            qdrant_filter = Filter(must=conditions)
            
            try:
                result = self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=qdrant_filter,
                )
                logger.info(f"Deleted documents matching filters (count unknown)")
                return -1  # Qdrant doesn't return count for filter-based deletion
            except Exception as e:
                logger.error(f"Failed to delete documents by filter: {e}")
                raise
        
        logger.warning("No document_ids or filters provided for deletion")
        return 0
    
    def count_documents(self) -> int:
        """Get total number of documents in the collection."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except Exception as e:
            logger.error(f"Failed to count documents: {e}")
            raise
    
    def delete_collection(self) -> None:
        """Delete the entire collection. Use with caution!"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.warning(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise


# Global document store instance
def get_document_store() -> QdrantDocumentStore:
    """Get or create the global document store instance."""
    return QdrantDocumentStore()