from pydantic import BaseSettings

class Settings(BaseSettings):
    # FastAPI settings
    title: str = "Haystack RAG Application"
    description: str = "A Retrieval-Augmented Generation application using Haystack and FastAPI."
    version: str = "1.0.0"

    # Document store settings
    document_store_type: str = "InMemory"  # Options: "InMemory", "Elasticsearch", etc.
    elasticsearch_host: str = "localhost"
    elasticsearch_port: int = 9200

    # Pipeline settings
    indexing_batch_size: int = 100
    retrieval_top_k: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()