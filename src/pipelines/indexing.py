"""
Indexing Pipeline for Document Processing

Processes documents through:
1. Text splitting (chunking)
2. Embedding generation
3. Writing to document store
"""

from typing import List
from haystack.core.pipeline import Pipeline
from haystack.dataclasses import Document
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret
from src.document_stores.store import QdrantDocumentStore
from src.config.settings import settings


def create_indexing_pipeline() -> Pipeline:
    """
    Create a Haystack 2.x indexing pipeline.
    
    Pipeline flow:
    1. DocumentSplitter - Splits documents into chunks
    2. OpenAIDocumentEmbedder - Creates embeddings for each chunk
    3. DocumentWriter - Writes documents with embeddings to Qdrant
    
    Returns:
        Pipeline: Configured indexing pipeline
    """
    # Initialize document store
    document_store = QdrantDocumentStore(
        collection_name=settings.qdrant_collection_name,
        embedding_dimension=settings.embedding_dimension
    )
    
    # Initialize pipeline components
    splitter = DocumentSplitter(
        split_by="word",
        split_length=settings.chunk_size,
        split_overlap=settings.chunk_overlap
    )
    
    embedder = OpenAIDocumentEmbedder(
        api_key=Secret.from_token(settings.openai_api_key),
        model=settings.embedding_model
    )
    
    writer = DocumentWriter(document_store=document_store)
    
    # Create and configure pipeline
    pipeline = Pipeline()
    pipeline.add_component("splitter", splitter)
    pipeline.add_component("embedder", embedder)
    pipeline.add_component("writer", writer)
    
    # Connect components
    pipeline.connect("splitter.documents", "embedder.documents")
    pipeline.connect("embedder.documents", "writer.documents")
    
    return pipeline


def index_documents(documents: List[Document]) -> dict:
    """
    Index documents through the pipeline.
    
    Args:
        documents: List of Haystack Document objects to index
        
    Returns:
        dict: Pipeline results with number of documents written
    """
    pipeline = create_indexing_pipeline()
    result = pipeline.run({"splitter": {"documents": documents}})
    return result
