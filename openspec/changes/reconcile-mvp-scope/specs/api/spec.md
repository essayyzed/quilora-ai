# Delta for API Specification - MVP Scope Reconciliation

## MODIFIED Requirements

### Requirement: Document Upload

**Status:** ⏳ DEFERRED TO PHASE 1.5

The system SHALL provide an endpoint to upload documents for indexing.

> **MVP Note:** This endpoint is not implemented in MVP. Documents can be indexed programmatically via the `index_documents()` function. API endpoint planned for Phase 1.5.

#### Scenario: Successful document upload

- GIVEN a user has a valid document file (PDF, TXT, MD, or DOCX)
- WHEN the user uploads the file via POST /documents
- THEN the system SHALL accept the file
- AND return a document_id
- AND index the document in the background
- AND return HTTP 201 Created

---

### Requirement: Document Listing

**Status:** ⏳ DEFERRED TO PHASE 1.5

The system SHALL provide an endpoint to list all indexed documents.

> **MVP Note:** Not implemented in MVP. Users can query Qdrant directly or use the document store's `count_documents()` method.

---

### Requirement: Document Deletion

**Status:** ⏳ DEFERRED TO PHASE 1.5

The system SHALL provide an endpoint to delete documents from the index.

> **MVP Note:** Not implemented in MVP. Documents can be deleted programmatically via `delete_documents()` method.

---

### Requirement: Query Endpoint

**Status:** ✅ IMPLEMENTED (Partial - Non-Streaming)

The system SHALL provide an endpoint for querying documents with AI-generated answers.

#### Scenario: Query without streaming ✅ IMPLEMENTED

- GIVEN documents are indexed in the system
- WHEN a user sends a query via POST /query
- THEN the system SHALL retrieve relevant document chunks
- AND generate a complete answer
- AND return the answer with source references as JSON
- AND return HTTP 200 OK

#### Scenario: Query with streaming ⏳ DEFERRED TO PHASE 2

- GIVEN documents are indexed in the system
- WHEN a user sends a query with stream=true
- THEN the system SHALL stream the AI-generated response via Server-Sent Events

> **MVP Note:** Streaming not implemented. All responses are synchronous JSON.

#### Scenario: Query with empty input ✅ IMPLEMENTED

- GIVEN a user sends an empty query
- WHEN the request is processed
- THEN the system SHALL return HTTP 400 Bad Request
- AND include error message "Query cannot be empty"

---

### Requirement: Health Check

**Status:** ⏳ DEFERRED TO PHASE 1.5

The system SHALL provide a health check endpoint.

> **MVP Note:** Not implemented. Monitoring relies on manual checks.

---

### Requirement: CORS Support

**Status:** ✅ IMPLEMENTED

The system SHALL support Cross-Origin Resource Sharing for frontend access.

> **MVP Note:** CORS is configured but not actively used since frontend is deferred.

---

### Requirement: Error Handling

**Status:** ✅ IMPLEMENTED (Enhanced)

The system SHALL handle errors securely without leaking internal details.

#### Scenario: Internal error handling ✅ IMPLEMENTED

- GIVEN an internal error occurs during query processing
- WHEN the error is caught
- THEN the system SHALL log the full exception with stack trace internally
- AND return HTTP 500 with generic message "Internal server error"
- AND NOT expose internal error details to client

> **MVP Note:** This security enhancement was added during code review improvements.
