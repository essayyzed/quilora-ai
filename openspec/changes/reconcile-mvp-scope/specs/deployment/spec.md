# Delta for Deployment Specification - MVP Scope Reconciliation

## MODIFIED Requirements

### Requirement: Docker Compose Orchestration

**Status:** ⏳ DEFERRED TO PHASE 2

The system SHALL provide Docker Compose for multi-service orchestration.

> **MVP Note:** Docker Compose not implemented. Current deployment is manual:
>
> 1. Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
> 2. Run API: `uv run uvicorn src.api.main:app --reload`

**Original Scope:**

- Docker Compose with Frontend, Backend, Qdrant services
- Volume mounts for data persistence
- Environment configuration via .env
- Health checks for all services
- Restart policies

**MVP Deployment:**

```bash
# Terminal 1: Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Terminal 2: API
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

---

### Requirement: Backend Dockerfile

**Status:** ⏳ DEFERRED TO PHASE 2

> **MVP Note:** No Dockerfile. Run directly with Python/uv.

---

### Requirement: Frontend Containerization

**Status:** ⏳ DEFERRED TO PHASE 3

> **MVP Note:** Depends on frontend implementation (Phase 3).

---

### Requirement: Health Checks

**Status:** ⏳ DEFERRED TO PHASE 2

> **MVP Note:** No automated health checks. Manual verification:
>
> - Qdrant: `curl http://localhost:6333/health`
> - API: `curl http://localhost:8000/`

---

### Requirement: Production Configuration

**Status:** ⏳ DEFERRED TO PHASE 2

> **MVP Note:** Development configuration only. Production would need:
>
> - Gunicorn/Uvicorn workers
> - Proper logging configuration
> - Secret management
> - SSL/TLS termination

---

## MVP Quick Start

### Prerequisites

1. Python 3.11+
2. Docker (for Qdrant)
3. OpenAI API key

### Setup

```bash
# Clone and setup
git clone <repo>
cd quilora-ai
uv sync

# Configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Start Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# Start API
uv run uvicorn src.api.main:app --reload

# Test
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'
```

---

## Phase 2 Deployment Plan

When implementing Docker Compose:

```yaml
# docker-compose.yml (planned)
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - '6333:6333'
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:6333/health']

  api:
    build: .
    ports:
      - '8000:8000'
    environment:
      - QDRANT_HOST=qdrant
    depends_on:
      qdrant:
        condition: service_healthy

volumes:
  qdrant_data:
```
