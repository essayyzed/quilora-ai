# Change: Reconcile MVP Scope with Implementation

## Status

**APPROVED** - Retroactive documentation of scope decisions

## Why

The original `implement-rag-application` proposal was ambitious, covering a full-stack RAG application with frontend, multiple LLM providers (via aisuite), streaming support, and Docker deployment. During implementation, the team made pragmatic decisions to focus on core backend functionality first, diverging from some original specifications.

This change formally documents those scope decisions and updates specifications to match the actual MVP implementation, creating alignment between specs and reality.

## What Changes

### Scope Adjustments (Not Breaking - Reducing Scope)

- **aisuite Integration** → Deferred to Phase 2; using OpenAI directly via Haystack's built-in components
- **Streaming Support** → Deferred to Phase 2; MVP uses synchronous responses
- **Vue 3 Frontend** → Deferred to Phase 3; API-only MVP
- **Docker Compose Deployment** → Deferred to Phase 2; manual deployment for MVP
- **Document Management Endpoints** → Moved to Phase 1.5 backlog

### What IS Implemented (MVP Core)

- ✅ Document Store with Qdrant (exceeds spec - includes caching, thread-safety)
- ✅ Configuration Management (100% complete)
- ✅ Indexing Pipeline (Haystack 2.x)
- ✅ Retrieval Pipeline with answer generation
- ✅ Query API endpoint (POST /query)
- ✅ Basic error handling and logging

### Rationale for Divergence

| Original Spec          | Implementation          | Reason                                                                                       |
| ---------------------- | ----------------------- | -------------------------------------------------------------------------------------------- |
| aisuite multi-provider | OpenAI via Haystack     | Haystack has excellent OpenAI integration; aisuite adds complexity without immediate benefit |
| Groq/Llama 3.3 primary | OpenAI primary          | OpenAI more reliable for initial development; Groq can be added later                        |
| SSE streaming          | Synchronous JSON        | Simpler implementation; streaming adds frontend complexity                                   |
| Full API (6 endpoints) | Query only (1 endpoint) | Focus on RAG core; document management can use CLI/scripts                                   |
| Vue 3 frontend         | None                    | API-first development; frontend is separate concern                                          |

## Impact

### Affected Specs

- `api/spec.md` - Mark unimplemented endpoints as "Phase 2"
- `llm-integration/spec.md` - Document OpenAI-only approach for MVP
- `pipelines/spec.md` - Mark streaming as "Phase 2"
- `frontend/spec.md` - Mark entire spec as "Phase 3"
- `deployment/spec.md` - Mark as "Phase 2"

### Affected Code

- No code changes required (documenting existing state)

## Success Criteria

- [ ] All delta specs updated to reflect MVP scope
- [ ] Original proposal marked as "MVP Complete"
- [ ] Clear phase roadmap documented
- [ ] Tasks.md updated with completion status

## Timeline

- Immediate (documentation only)

## Phase Roadmap

### Phase 1: MVP Core ✅ COMPLETE

- Document store integration
- Indexing pipeline
- Retrieval pipeline with answer generation
- Query API endpoint
- Configuration management
- Basic tests

### Phase 1.5: Document Management API (Next)

- POST /documents (upload)
- GET /documents (list)
- DELETE /documents/{id}
- GET /health

### Phase 2: Production Readiness

- Streaming support (SSE)
- Docker Compose deployment
- Retry logic with exponential backoff
- Comprehensive monitoring
- CI/CD pipeline

### Phase 3: Advanced Features

- Vue 3 frontend
- aisuite integration (multi-provider)
- Authentication/authorization
- Advanced document processing (OCR, tables)
