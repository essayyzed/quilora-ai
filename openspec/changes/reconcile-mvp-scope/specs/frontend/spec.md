# Delta for Frontend Specification - MVP Scope Reconciliation

## MODIFIED Requirements

### Requirement: Vue 3 Frontend Application

**Status:** ⏳ DEFERRED TO PHASE 3

The system SHALL provide a Vue 3 frontend for user interaction.

> **MVP Note:** Frontend is not implemented. MVP is API-only. All interaction is via:
>
> - Direct API calls (curl, Postman)
> - FastAPI's built-in /docs (Swagger UI)
> - Python scripts using the API or pipeline functions directly

**Original Scope:**

- Vue 3 with Composition API
- TypeScript
- Chat interface component
- Document upload UI
- Document list management
- SSE streaming for responses
- Vite build tooling

**MVP Alternative:**

- FastAPI /docs endpoint for interactive API testing
- Example scripts in `examples/` directory
- Direct pipeline function calls for development

---

### Requirement: Chat Interface

**Status:** ⏳ DEFERRED TO PHASE 3

> **MVP Note:** Users can send queries via POST /query using any HTTP client.

---

### Requirement: Document Upload UI

**Status:** ⏳ DEFERRED TO PHASE 3

> **MVP Note:** Documents are indexed programmatically. See `examples/test_qdrant_basic.py` for usage.

---

### Requirement: SSE Streaming Display

**Status:** ⏳ DEFERRED TO PHASE 3

> **MVP Note:** Depends on streaming support (Phase 2) and frontend (Phase 3).

---

## Future Implementation Notes

When implementing frontend in Phase 3:

1. **Tech Stack:** Vue 3 + TypeScript + Vite (as originally specified)
2. **Dependencies:**
   - Phase 2 streaming support must be complete
   - Document management API (Phase 1.5) must be complete
3. **Estimated Effort:** 2-3 weeks
4. **Key Components:**
   - ChatView.vue - Query interface with response display
   - DocumentUpload.vue - File upload with progress
   - DocumentList.vue - Manage indexed documents
   - API service with SSE client
