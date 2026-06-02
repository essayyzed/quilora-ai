# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Quilora** is a production-ready Retrieval-Augmented Generation (RAG) application that enables users to query documents using natural language. It combines the speed and cost-efficiency of small language models (Groq/Llama 3.3) with the flexibility to scale to frontier models (OpenAI, Anthropic Claude) when needed.

Core capabilities:
- Document upload and indexing via REST API
- Semantic search with RAG-powered answers
- Real-time token streaming via Server-Sent Events (SSE)
- Multi-provider LLM support with automatic fallback chains
- Health monitoring and observability with structured logging
- Production-ready with Docker, CI/CD, and comprehensive error handling

## Architecture Overview

### High-Level Design

The application follows a layered architecture with three main components:

1. **API Layer** (`src/api/`): FastAPI REST endpoints for document management (`/documents`) and queries (`/query`). The logging middleware adds request tracing with X-Request-ID headers and performance timing for all requests.

2. **Processing Layer** (`src/pipelines/`, `src/llm/`): Haystack 2.x pipelines handle the RAG workflow:
   - **Indexing Pipeline**: Documents → chunks → embeddings → Qdrant storage
   - **Retrieval Pipeline**: Query → embedding → vector search → LLM generation (with streaming support)
   - **LLM Routing**: Intelligent provider selection (via `router.py`) and query complexity classification (via `classifier.py`) that routes simple queries to Groq, moderate to OpenAI, and complex to Anthropic

3. **Storage Layer** (`src/document_stores/`): Custom `QdrantDocumentStore` wraps the Qdrant vector database with batching, metadata filtering, and document CRUD operations.

### Key Design Patterns

- **Singleton caching**: Embedders, document stores, and registries are cached to avoid expensive reconnections
- **Provider registry**: `LLMProviderRegistry` tracks health status, error rates, and availability for all LLM providers via aisuite
- **Automatic fallback chains**: If primary LLM fails, router automatically attempts fallback providers based on strategy (speed/balanced/quality)
- **Retry with exponential backoff**: Transient failures (OpenAI, Qdrant) use tenacity decorators with configurable retry counts and wait times
- **Streaming generator**: `retrieve_documents_streaming()` yields token events for real-time frontend updates

### Data Flow Example: Query Processing

1. Client POSTs `/query` with query text and optional `provider` override
2. Logging middleware captures request, generates unique ID
3. Router classifies query complexity and selects provider (unless overridden)
4. Query embedding generated via OpenAI (with 3-attempt retry on failure)
5. Qdrant searched for similar documents (with 2-attempt retry)
6. LLM called with prompt + retrieved context (with fallback chain if primary fails)
7. Response streamed via SSE if `stream=true`, otherwise returned as JSON
8. Performance metrics (embedding_ms, search_ms, generation_ms, total_ms) included in response

## Development Workflow

### Commands

**Setup**
```bash
# Install dependencies
uv sync

# Copy environment template and add your API keys
cp .env.example .env
# Edit .env with OPENAI_API_KEY, GROQ_API_KEY, ANTHROPIC_API_KEY
```

**Running**
```bash
# Start Qdrant (required for all operations)
docker run -p 6333:6333 qdrant/qdrant

# Development server with hot reload
.venv/bin/python3 -m uvicorn src.api.main:app --reload

# Production via Docker Compose
docker-compose up --build -d
docker-compose logs -f api
```

**Testing**
```bash
# All tests (requires Qdrant running)
uv run pytest -v

# Specific test file
uv run pytest tests/test_llm_router.py -v

# Single test function
uv run pytest tests/test_llm_router.py::test_select_provider -v

# With coverage report
uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html

# Only integration tests (marked with @pytest.mark.integration)
uv run pytest -m integration -v

# Skip integration tests (fast unit tests only)
uv run pytest -m "not integration" -v
```

**Code Quality**
```bash
# Format code
uv run black src/ tests/

# Sort imports
uv run isort src/ tests/

# Lint with ruff
uv run ruff check src/ tests/

# All together
uv run black src/ tests/ && uv run isort src/ tests/ && uv run ruff check src/ tests/
```

**API Testing**
```bash
# View interactive API docs
curl http://localhost:8000/docs

# Health check
curl http://localhost:8000/health

# Stream a query
curl -N -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "stream": true}'

# Upload a document
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{"content": "My document text here", "metadata": {"source": "manual"}}'
```

## Configuration & Settings

All configuration lives in `src/config/settings.py` as a Pydantic BaseSettings class. Settings are loaded from `.env` file and environment variables, with defaults that work for local development.

**Critical Settings to Know**
- `OPENAI_API_KEY`: Required for embeddings (text-embedding-3-small) and fallback LLM
- `GROQ_API_KEY`: Primary LLM provider (Llama 3.3 70B) - free tier available
- `ANTHROPIC_API_KEY`: Optional, used for complex queries when enabled
- `QDRANT_HOST` / `QDRANT_PORT`: Local Qdrant connection (default localhost:6333)
- `LLM_PROVIDER_STRATEGY`: "speed" (Groq-first) | "balanced" (default) | "quality" (Anthropic-first)
- `CHUNK_SIZE` / `CHUNK_OVERLAP`: Document chunking parameters (512/50 tokens default)
- `RETRIEVAL_TOP_K`: Number of document chunks to retrieve (5 default)
- `MIN_SIMILARITY_SCORE`: Minimum relevance threshold for retrieved documents (0.5 default)
- `LLM_TEMPERATURE`: 0.0 for deterministic answers (production), higher for creative responses
- `LOG_LEVEL`: DEBUG | INFO | WARNING | ERROR | CRITICAL (INFO default)

## Important Code Locations

**API Routes**: `src/api/routes/`
- `query.py`: `/query` endpoint with streaming and non-streaming support
- `documents.py`: `/documents` CRUD endpoints for document management
- `health.py`: `/health` endpoint with provider health status and uptime

**LLM System**: `src/llm/`
- `provider.py`: `LLMProviderRegistry` with health tracking for all providers
- `router.py`: `ProviderRouter` that selects optimal provider based on strategy + complexity
- `classifier.py`: `QueryComplexityClassifier` that heuristically categorizes queries (simple/moderate/complex)

**RAG Pipelines**: `src/pipelines/`
- `indexing.py`: `create_indexing_pipeline()` builds Haystack pipeline for document chunking → embedding → storage
- `retrieval.py`: `retrieve_documents()` and `retrieve_documents_streaming()` handle full RAG flow with retry logic and performance timing

**Vector Storage**: `src/document_stores/store.py`
- `QdrantDocumentStore`: Wraps Qdrant client with connection pooling, batching, and Haystack-compatible document operations

**Request Context**: `src/middleware/logging.py`
- `LoggingMiddleware`: Adds request ID (X-Request-ID header) and timing to all requests
- `configure_logging()`: Structured logging setup

## Testing Strategy

Tests are organized by concern:
- `test_llm_provider.py`: Tests provider registry initialization and health tracking
- `test_llm_router.py`: Tests intelligent provider selection logic
- `test_llm_classifier.py`: Tests query complexity classification heuristics
- `test_document_store.py`: Tests Qdrant CRUD operations
- `test_documents.py`: Tests document management API endpoints
- `test_api.py`: End-to-end API tests
- `test_pipelines.py`: Integration tests for Haystack pipelines

Key testing patterns:
- Use `conftest.py` for shared fixtures (mock settings, test documents, Qdrant connection)
- Mock external services (OpenAI, Groq, Anthropic) to avoid API calls during tests
- Integration tests marked with `@pytest.mark.integration` require running Qdrant
- Test files mirror `src/` structure for easy navigation

## Phase Context

This project uses a phased development approach documented in `docs/PHASE2_COMPLETION.md`:

**Phase 1** (Complete): Foundation - FastAPI, Haystack 2.x, Qdrant integration, basic RAG pipeline
**Phase 2** (Complete): Production Readiness - Streaming via SSE, retry logic with exponential backoff, performance timing, logging middleware, health checks, Docker/Compose, CI/CD
**Phase 3** (In Progress): Multi-LLM Support - aisuite integration for Groq/OpenAI/Anthropic routing, query complexity classification, cost-aware provider selection

For new features, check `openspec/changes/` directory for change proposal structure and convention. If proposing new capabilities or breaking changes, create a change proposal document following the OpenSpec pattern.

## Common Task Patterns

**Adding a New LLM Provider**
1. Add API key to `.env` (e.g., `NEW_PROVIDER_API_KEY`)
2. Update `src/config/settings.py` with field for key and model configuration
3. Update `src/llm/provider.py` to initialize provider in registry
4. Update `src/llm/router.py` fallback chains and preference matrix for the new provider
5. Tests automatically pick up new provider if health tracking added

**Adding Document Processing Feature** (e.g., new file type)
1. Update `SUPPORTED_EXTENSIONS` in `src/api/routes/documents.py`
2. Add file extraction logic (already supports TXT, MD, PDF via PyPDF2, DOCX via python-docx)
3. Test with `test_documents.py`

**Modifying RAG Behavior**
1. Change settings in `src/config/settings.py` (e.g., chunk size, top_k, similarity threshold)
2. Update prompt template in `src/pipelines/retrieval.py` if changing answer generation
3. Adjust retry logic via settings: `openai_max_retries`, `qdrant_max_retries`, `retry_min_wait_seconds`, `retry_max_wait_seconds`
4. Update complexity classifier thresholds in `src/llm/classifier.py` if tuning provider routing

**Debugging LLM Routing**
- Set `LOG_LEVEL=DEBUG` to see detailed routing decisions
- Check health endpoint (`/health`) to see which providers are available
- Logs show: query complexity classification, provider selection reason, fallback chain attempts
- `src/llm/provider.py` tracks error rates and failure reasons in registry

## Documentation

- `README.md`: Quick start, setup, API examples
- `docs/architecture.md`: System design, component details, data flows, deployment architecture, observability
- `docs/troubleshooting.md`: Common issues and diagnostic solutions
- `docs/PHASE2_COMPLETION.md`: Detailed summary of Phase 2 implementation with file changes and test results

## Environment Variables (Key)

See `.env.example` for complete list. Essentials:
- `OPENAI_API_KEY` (required)
- `GROQ_API_KEY` (required for production, optional if other providers configured)
- `ANTHROPIC_API_KEY` (optional)
- `QDRANT_HOST`, `QDRANT_PORT` (default: localhost:6333)
- `PRIMARY_LLM_PROVIDER`, `FALLBACK_LLM_PROVIDER`, `PREMIUM_LLM_PROVIDER` (format: "provider:model")
- `LLM_PROVIDER_STRATEGY` (speed | balanced | quality)

## Git Conventions

- Feature branches: `feat/description`
- Bugfix branches: `bugfix/description`
- Commit messages: `feat:`, `fix:`, `docs:`, `refactor:`, `test:` prefixes
- All changes to main require passing tests and linting
