# Change: Add Document Management API (Phase 1.5)

## Why

The MVP provides core RAG functionality (indexing, retrieval, answer generation) but requires programmatic access to manage documents. Users must write Python scripts to add/remove documents, which is friction for adoption and testing.

Adding document management endpoints makes the API self-contained and enables:

- Document upload via HTTP (no Python scripting required)
- Document listing for inventory/debugging
- Document deletion for content management
- Health check for monitoring and deployment validation

## What Changes

- **API Endpoints:** Add 4 new endpoints
  - `GET /health` - Health check with dependency status
  - `POST /documents` - Upload and index documents
  - `GET /documents` - List indexed documents with metadata
  - `DELETE /documents/{id}` - Remove documents from index
- **Schemas:** Add Pydantic models for document operations
- **Routes:** New `documents.py` router module

## Impact

- **Affected specs:** `api` (primary)
- **Affected code:**
  - `src/api/main.py` - Register new router
  - `src/api/routes/documents.py` - New file
  - `src/api/routes/health.py` - New file
  - `src/api/schemas/documents.py` - New file
- **No breaking changes** - Additive only

## Success Criteria

1. All 4 endpoints return correct HTTP status codes
2. Document upload triggers indexing pipeline
3. Health check verifies Qdrant connectivity
4. Tests cover success and error scenarios
5. OpenAPI documentation auto-generated
