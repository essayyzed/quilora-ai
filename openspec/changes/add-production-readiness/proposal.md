# Change: Production Readiness (Phase 2)

## Why

Phase 1 and Phase 1.5 delivered a functional RAG API with core document management, but the system lacks production-grade features needed for deployment:

- **No containerization** - Manual deployment is error-prone and environment-dependent
- **No streaming** - Query responses require users to wait for full LLM generation
- **Limited observability** - No structured logging, request tracking, or performance metrics
- **No CI/CD** - Manual testing and deployment increases risk of regressions
- **No production configuration** - Missing rate limiting, request validation, timeouts

Phase 2 adds production readiness while maintaining the simple deployment model.

## What Changes

### Streaming Responses
- **API:** Add SSE (Server-Sent Events) support to `/query` endpoint
- **Pipeline:** Integrate streaming OpenAIGenerator
- **Schema:** Add `stream` parameter to QueryRequest

### Docker & Orchestration
- **Backend Dockerfile:** Multi-stage build with production optimizations
- **Docker Compose:** Orchestrate FastAPI + Qdrant with proper networking
- **Environment:** Secure secrets management via .env
- **Volumes:** Persistent Qdrant data

### Observability
- **Structured Logging:** JSON logs with request IDs, timing, metadata
- **Request Tracking:** Correlation IDs across pipeline stages
- **Performance Metrics:** Track embedding time, retrieval latency, generation time
- **Health Monitoring:** Enhanced health check with component status

### CI/CD
- **GitHub Actions:** Automated testing on push/PR
- **Linting:** Black, isort, ruff for code quality
- **Test Coverage:** Enforce minimum coverage thresholds

### Documentation
- **Architecture Diagram:** System component visualization
- **Troubleshooting Guide:** Common issues and solutions
- **Deployment Guide:** Production deployment best practices

## Impact

**Affected specs:**
- `api` - Streaming support, logging middleware
- `pipelines` - Streaming LLM integration
- `deployment` - Docker, CI/CD configuration

**Affected code:**
- `src/api/routes/query.py` - Add streaming endpoint
- `src/pipelines/retrieval.py` - Support streaming mode
- `src/api/main.py` - Add logging middleware
- `Dockerfile` - New file
- `docker-compose.yml` - New file
- `.github/workflows/` - New CI/CD workflows
- `pyproject.toml` - Add dev dependencies (black, ruff)

**No breaking changes** - All additive features with backward compatibility.

## Success Criteria

1. ✅ Query streaming returns incremental tokens via SSE
2. ✅ Docker Compose brings up entire stack with one command
3. ✅ Structured logs include request IDs and timing
4. ✅ CI runs tests automatically on every push
5. ✅ Code passes linting checks (black, ruff)
6. ✅ Architecture diagram documents system components
7. ✅ All existing tests continue to pass
