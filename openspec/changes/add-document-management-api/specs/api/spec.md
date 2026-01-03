# Delta for API Specification - Document Management API (Phase 1.5)

## ADDED Requirements

### Requirement: Health Check Endpoint

The system SHALL provide a health check endpoint for monitoring and deployment validation.

#### Scenario: All services healthy

- GIVEN Qdrant is accessible
- WHEN a request is made to GET /health
- THEN the system SHALL return HTTP 200 OK
- AND include JSON with `status: "healthy"`
- AND include `qdrant: "connected"`
- AND include `timestamp` in ISO format

#### Scenario: Qdrant unavailable

- GIVEN Qdrant is not accessible
- WHEN a request is made to GET /health
- THEN the system SHALL return HTTP 503 Service Unavailable
- AND include JSON with `status: "unhealthy"`
- AND include `qdrant: "disconnected"`
- AND include error details

---

### Requirement: Document Upload Endpoint

The system SHALL provide an endpoint to upload and index documents.

#### Scenario: Upload text content

- GIVEN a user provides text content with metadata
- WHEN the user sends POST /documents with JSON body
- THEN the system SHALL create a Document object
- AND run the indexing pipeline
- AND return HTTP 201 Created
- AND return the document_id and chunk_count

#### Scenario: Upload file

- GIVEN a user uploads a file (TXT, MD, or PDF)
- WHEN the user sends POST /documents/upload as multipart/form-data
- THEN the system SHALL read the file content
- AND create a Document object with filename as metadata
- AND run the indexing pipeline
- AND return HTTP 201 Created
- AND return the document_id and chunk_count

#### Scenario: Empty content

- GIVEN a user provides empty content
- WHEN the request is processed
- THEN the system SHALL return HTTP 400 Bad Request
- AND include error message "Content cannot be empty"

#### Scenario: Unsupported file type

- GIVEN a user uploads an unsupported file type
- WHEN the request is processed
- THEN the system SHALL return HTTP 400 Bad Request
- AND include error message listing supported formats

---

### Requirement: Document Listing Endpoint

The system SHALL provide an endpoint to list indexed documents.

#### Scenario: List all documents

- GIVEN documents exist in the vector store
- WHEN a user requests GET /documents
- THEN the system SHALL return HTTP 200 OK
- AND return a list of documents with id, metadata, and content preview
- AND include total_count

#### Scenario: No documents

- GIVEN no documents exist in the vector store
- WHEN a user requests GET /documents
- THEN the system SHALL return HTTP 200 OK
- AND return an empty list
- AND include total_count of 0

#### Scenario: Pagination

- GIVEN many documents exist in the vector store
- WHEN a user requests GET /documents?limit=10&offset=20
- THEN the system SHALL return HTTP 200 OK
- AND return at most 10 documents starting from offset 20
- AND include total_count for all documents

---

### Requirement: Document Deletion Endpoint

The system SHALL provide an endpoint to delete documents from the index.

#### Scenario: Delete by document ID

- GIVEN a document with the specified ID exists
- WHEN a user requests DELETE /documents/{document_id}
- THEN the system SHALL remove the document from the vector store
- AND return HTTP 200 OK
- AND return confirmation with deleted document_id

#### Scenario: Delete non-existent document

- GIVEN no document with the specified ID exists
- WHEN a user requests DELETE /documents/{document_id}
- THEN the system SHALL return HTTP 404 Not Found
- AND include error message "Document not found"

#### Scenario: Delete all documents

- GIVEN documents exist in the vector store
- WHEN a user requests DELETE /documents with query param ?all=true
- THEN the system SHALL remove all documents
- AND return HTTP 200 OK
- AND return count of deleted documents
