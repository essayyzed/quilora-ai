# Implementation Tasks

**Status:** MVP COMPLETE ✅ (Phase 1 only)  
**Last Updated:** January 3, 2026  
**Reconciliation:** See `openspec/changes/reconcile-mvp-scope/` for scope adjustments

---

## 1. Environment Setup ✅ COMPLETE

- [x] 1.1 Update requirements.txt with all dependencies (haystack, qdrant-client, fastapi, uvicorn, etc.)
- [x] 1.2 Create .env.example with required environment variables (API keys, Qdrant URL, etc.)
- [x] 1.3 Update pyproject.toml with project metadata and dependencies
- [x] 1.4 Set up Python virtual environment configuration

## 2. Configuration Management ✅ COMPLETE

- [x] 2.1 Implement settings.py with Pydantic Settings for environment-based configuration
- [x] 2.2 Add configuration for Qdrant connection (host, port, collection name)
- [x] 2.3 ~~Add configuration for aisuite~~ → Using OpenAI directly (see reconcile-mvp-scope)
- [x] 2.4 Add configuration for embedding model selection
- [x] 2.5 Add configuration for document processing (chunk size, overlap)

## 3. Document Store Integration ✅ COMPLETE

- [x] 3.1 Implement Qdrant document store wrapper in src/document_stores/store.py
- [x] 3.2 Create document store initialization with collection setup
- [x] 3.3 Implement document upsert and delete methods
- [x] 3.4 Add document retrieval with similarity search
- [x] 3.5 Write tests for document store operations
- [x] 3.6 **ENHANCEMENT:** Add thread-safe singleton pattern (code review improvement)
- [x] 3.7 **ENHANCEMENT:** Add reserved keys protection (code review improvement)

## 4. LLM Integration ⏳ DEFERRED TO PHASE 3

> **Note:** Using OpenAI directly via Haystack instead of aisuite. See `reconcile-mvp-scope` for rationale.

- [ ] 4.1 ~~Create aisuite client wrapper~~ → Phase 3
- [ ] 4.2 ~~Implement Haystack-compatible LLM component using aisuite~~ → Phase 3
- [ ] 4.3 ~~Add support for streaming responses~~ → Phase 2
- [ ] 4.4 ~~Implement token counting and rate limiting logic~~ → Phase 2
- [ ] 4.5 ~~Add error handling and fallback mechanisms~~ → Phase 3
- [ ] 4.6 ~~Write tests for LLM component with mocked responses~~ → Phase 3

**MVP Implementation:**

- [x] Using Haystack's built-in OpenAIGenerator
- [x] Basic error handling (logs internally, generic client message)

## 5. Indexing Pipeline ✅ COMPLETE

- [x] 5.1 ~~Implement document preprocessing~~ → Documents passed as Haystack objects
- [x] 5.2 Create text chunking component (DocumentSplitter)
- [x] 5.3 Set up embedding component (OpenAIDocumentEmbedder)
- [x] 5.4 Build indexing pipeline in src/pipelines/indexing.py
- [x] 5.5 Add pipeline validation and error handling (basic)
- [x] 5.6 Write integration tests for indexing pipeline

## 6. Retrieval Pipeline ✅ COMPLETE (Non-Streaming)

- [x] 6.1 Implement query embedding component (OpenAITextEmbedder with caching)
- [x] 6.2 Create retriever component connected to Qdrant
- [x] 6.3 Implement prompt builder component (PromptBuilder)
- [x] 6.4 ~~Integrate aisuite LLM~~ → Using OpenAIGenerator
- [x] 6.5 Build complete retrieval pipeline in src/pipelines/retrieval.py
- [ ] 6.6 ~~Add support for context windowing and token management~~ → Phase 2
- [x] 6.7 Write integration tests for retrieval pipeline

## 7. FastAPI Backend ⚠️ PARTIAL (1/6 endpoints)

- [x] 7.1 Set up FastAPI application in src/api/main.py
- [ ] 7.2 ~~Implement health check endpoint (GET /health)~~ → Phase 1.5
- [ ] 7.3 ~~Implement document upload endpoint (POST /documents)~~ → Phase 1.5
- [ ] 7.4 ~~Implement document list endpoint (GET /documents)~~ → Phase 1.5
- [ ] 7.5 ~~Implement document delete endpoint (DELETE /documents/{id})~~ → Phase 1.5
- [x] 7.6 Implement query endpoint (POST /query) - **Non-streaming**
- [x] 7.7 Add CORS middleware for frontend access (configured)
- [x] 7.8 Implement error handling middleware (secure, no leaks)
- [ ] 7.9 ~~Add request logging and monitoring~~ → Phase 2
- [x] 7.10 Write API tests using TestClient

## 8. API Schemas ✅ COMPLETE (Query only)

- [ ] 8.1 ~~Define DocumentUploadRequest schema~~ → Phase 1.5
- [ ] 8.2 ~~Define DocumentResponse schema~~ → Phase 1.5
- [x] 8.3 Define QueryRequest schema in src/api/schemas/query.py
- [x] 8.4 Define QueryResponse schema (non-streaming)
- [x] 8.5 Define error responses (HTTPException with detail)

## 9. Vue 3 Frontend ⏳ DEFERRED TO PHASE 3

> **Note:** MVP is API-only. Use FastAPI /docs for testing.

- [ ] 9.1 ~~Initialize Vue 3 project~~ → Phase 3
- [ ] 9.2 ~~Set up project structure~~ → Phase 3
- [ ] 9.3 ~~Create ChatView component~~ → Phase 3
- [ ] 9.4 ~~Create DocumentUpload component~~ → Phase 3
- [ ] 9.5 ~~Create MessageList component~~ → Phase 3
- [ ] 9.6 ~~Create QueryInput component~~ → Phase 3
- [ ] 9.7 ~~Implement API service layer~~ → Phase 3
- [ ] 9.8 ~~Add SSE handling~~ → Phase 3
- [ ] 9.9 ~~Implement error handling~~ → Phase 3
- [ ] 9.10 ~~Add styling~~ → Phase 3

## 10. Docker Configuration ⏳ DEFERRED TO PHASE 2

> **Note:** Using manual deployment for MVP.

- [ ] 10.1 ~~Create Dockerfile for FastAPI backend~~ → Phase 2
- [ ] 10.2 ~~Create Dockerfile for Vue frontend~~ → Phase 3
- [ ] 10.3 ~~Create docker-compose.yml~~ → Phase 2
- [ ] 10.4 ~~Configure environment variables~~ → Phase 2
- [ ] 10.5 ~~Add volumes for persistent data~~ → Phase 2
- [ ] 10.6 ~~Set up networking~~ → Phase 2
- [ ] 10.7 ~~Add health checks~~ → Phase 2
- [ ] 10.8 ~~Create .dockerignore~~ → Phase 2

## 11. Testing & Quality ⚠️ PARTIAL

- [x] 11.1 Unit tests exist (11/11 passing)
- [x] 11.2 Integration tests for API and pipelines
- [ ] 11.3 ~~Add linting configuration~~ → Phase 2
- [ ] 11.4 ~~Add frontend linting~~ → Phase 3
- [x] 11.5 Example scripts created (examples/test_qdrant_basic.py)
- [ ] 11.6 ~~Add CI/CD configuration~~ → Phase 2

## 12. Documentation ⚠️ PARTIAL

- [x] 12.1 Update README.md with project overview
- [x] 12.2 API docs via FastAPI /docs (auto-generated)
- [ ] 12.3 ~~Add architecture diagram~~ → Phase 2
- [x] 12.4 Environment variables documented in .env.example
- [ ] 12.5 ~~Add troubleshooting guide~~ → Phase 2
- [x] 12.6 Example usage in examples/ directory
- [x] 12.7 **ADDED:** OpenSpec audit and reconciliation docs

## 13. Deployment Preparation ⏳ DEFERRED TO PHASE 2

- [ ] 13.1 ~~Docker Compose brings up all services~~ → Phase 2
- [x] 13.2 Document indexing workflow tested (via scripts)
- [x] 13.3 Query and answer generation tested (via API tests)
- [ ] 13.4 ~~Streaming responses work correctly~~ → Phase 2
- [ ] 13.5 ~~LLM provider switching~~ → Phase 3
- [ ] 13.6 ~~Performance testing~~ → Phase 2
- [x] 13.7 Security review (secure error handling, no leaks)

---

## Summary

| Phase                    | Status         | Completion             |
| ------------------------ | -------------- | ---------------------- |
| Phase 1 (MVP Core)       | ✅ COMPLETE    | ~40% of original scope |
| Phase 1.5 (Document API) | ⏳ NOT STARTED | 0%                     |
| Phase 2 (Production)     | ⏳ NOT STARTED | 0%                     |
| Phase 3 (Advanced)       | ⏳ NOT STARTED | 0%                     |

**MVP delivers:** Core RAG functionality (indexing, retrieval, answer generation) via API.

**Deferred:** Document management API, streaming, frontend, Docker, aisuite multi-provider.
