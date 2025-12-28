# Project Context

## Purpose
**Quilora** ("Ask your documents anything") is a production-ready Retrieval-Augmented Generation (RAG) application that enables users to query their documents using natural language. The system indexes documents, retrieves relevant context, and generates answers using a hybrid LLM approach that balances cost, speed, and quality.

## Tech Stack

### Backend
- **Python 3.11+**: Core programming language
- **Haystack 2.x**: RAG pipeline framework for indexing and retrieval
- **FastAPI**: REST API framework with async support
- **aisuite**: Unified LLM interface for provider flexibility
- **LLM Strategy**: Hybrid approach
  - Primary: Groq (Llama 3.3 70B) - Free, fast, excellent for RAG
  - Fallback: OpenAI GPT-4o-mini - Cost-effective backup ($0.15/1M tokens)
  - Premium: Anthropic Claude 3.5 Sonnet - For complex queries
- **Qdrant**: Vector database for document storage and similarity search
- **Pydantic**: Data validation and settings management

### Frontend
- **Vue 3**: Frontend framework with Composition API
- **TypeScript**: Type-safe frontend development
- **Vite**: Build tool and dev server

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Poetry/pip**: Python dependency management

## Project Conventions

### Code Style
- **Python**: Follow PEP 8, use Black formatter (line length: 100)
- **Type hints**: Required for all function signatures
- **Docstrings**: Google-style docstrings for all public functions and classes
- **Vue/TypeScript**: ESLint + Prettier, 2-space indentation
- **File naming**: snake_case for Python, kebab-case for Vue components

### Architecture Patterns
- **Dependency Injection**: Use FastAPI's dependency injection for services
- **Repository Pattern**: Abstract data access through document store interface
- **Pipeline Pattern**: Use Haystack's pipeline architecture for RAG workflows
- **Configuration**: Environment-based configuration with Pydantic Settings
- **Error Handling**: Structured error responses with proper HTTP status codes

### Testing Strategy
- **Unit Tests**: pytest for business logic and utilities
- **Integration Tests**: Test Haystack pipelines with test fixtures
- **API Tests**: FastAPI TestClient for endpoint testing
- **Coverage Target**: Minimum 80% code coverage
- **Test Structure**: Mirror src/ structure in tests/

### Git Workflow
- **Branching**: feature/*, bugfix/*, hotfix/* from main
- **Commits**: Conventional commits (feat:, fix:, docs:, etc.)
- **PRs**: Require review before merge to main
- **CI**: Run tests and linting on all PRs

## Domain Context
- **RAG Workflow**: Document ingestion → chunking → embedding → vector storage → semantic search → LLM generation
- **Document Types**: Support PDF, TXT, MD, DOCX initially
- **Query Types**: Question answering, document summarization, information extraction
- **Context Window**: Manage token limits across different LLM providers
- **Streaming**: Support real-time response streaming for better UX

## Important Constraints
- **LLM Provider Flexibility**: Must support switching between providers (OpenAI, Anthropic, etc.) without code changes
- **Cost Management**: Implement token tracking and rate limiting
- **Data Privacy**: User documents stored locally or in controlled infrastructure
- **Response Time**: Target <3s for retrieval, streaming for generation
- **Scalability**: Design for horizontal scaling (stateless API)

## External Dependencies
- **aisuite**: Unified LLM interface (supports 15+ providers)
- **Groq**: Primary LLM provider - Llama 3.3 70B (free tier, 300+ tokens/sec)
- **OpenAI**: Embeddings (text-embedding-3-small) + fallback LLM (GPT-4o-mini)
- **Anthropic**: Premium LLM option (Claude 3.5 Sonnet)
- **Qdrant**: Vector database (self-hosted via Docker)
- **Embedding Models**: OpenAI text-embedding-3-small (1536 dim) or sentence-transformers
