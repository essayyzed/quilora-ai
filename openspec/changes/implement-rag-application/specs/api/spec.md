# Delta for API Specification

## ADDED Requirements

### Requirement: Document Upload
The system SHALL provide an endpoint to upload documents for indexing.

#### Scenario: Successful document upload
- GIVEN a user has a valid document file (PDF, TXT, MD, or DOCX)
- WHEN the user uploads the file via POST /documents
- THEN the system SHALL accept the file
- AND return a document_id
- AND index the document in the background
- AND return HTTP 201 Created

#### Scenario: Invalid file type
- GIVEN a user attempts to upload an unsupported file type
- WHEN the upload request is made
- THEN the system SHALL reject the file
- AND return HTTP 400 Bad Request
- AND include an error message indicating supported formats

#### Scenario: File size limit
- GIVEN a user attempts to upload a file larger than 10MB
- WHEN the upload request is made
- THEN the system SHALL reject the file
- AND return HTTP 413 Payload Too Large

### Requirement: Document Listing
The system SHALL provide an endpoint to list all indexed documents.

#### Scenario: List documents
- GIVEN documents are indexed in the system
- WHEN a user requests GET /documents
- THEN the system SHALL return a list of all documents
- AND include document_id, filename, upload timestamp, and chunk count
- AND return HTTP 200 OK

### Requirement: Document Deletion
The system SHALL provide an endpoint to delete documents from the index.

#### Scenario: Delete existing document
- GIVEN a document with document_id exists
- WHEN a user requests DELETE /documents/{document_id}
- THEN the system SHALL remove the document from the vector store
- AND return HTTP 200 OK
- AND include confirmation status

#### Scenario: Delete non-existent document
- GIVEN a document_id does not exist
- WHEN a user requests DELETE /documents/{document_id}
- THEN the system SHALL return HTTP 404 Not Found

### Requirement: Query Endpoint
The system SHALL provide an endpoint for querying documents with AI-generated answers.

#### Scenario: Query with streaming
- GIVEN documents are indexed in the system
- WHEN a user sends a query with stream=true
- THEN the system SHALL retrieve relevant document chunks
- AND stream the AI-generated response via Server-Sent Events
- AND return HTTP 200 OK

#### Scenario: Query without streaming
- GIVEN documents are indexed in the system
- WHEN a user sends a query with stream=false
- THEN the system SHALL retrieve relevant document chunks
- AND generate a complete answer
- AND return the answer with source references as JSON
- AND return HTTP 200 OK

#### Scenario: Query with no relevant documents
- GIVEN no relevant documents are found for the query
- WHEN a user sends a query
- THEN the system SHALL return a response indicating insufficient context
- AND suggest uploading relevant documents

### Requirement: Health Check
The system SHALL provide a health check endpoint.

#### Scenario: All services healthy
- GIVEN all dependencies are operational
- WHEN a request is made to GET /health
- THEN the system SHALL return HTTP 200 OK
- AND include status for Qdrant and LLM provider

#### Scenario: Service degraded
- GIVEN one or more dependencies are unavailable
- WHEN a request is made to GET /health
- THEN the system SHALL return HTTP 503 Service Unavailable
- AND indicate which services are down

### Requirement: CORS Support
The system SHALL support Cross-Origin Resource Sharing for frontend access.

#### Scenario: Frontend requests
- GIVEN a request originates from the configured frontend origin
- WHEN the request is made to any API endpoint
- THEN the system SHALL include appropriate CORS headers
- AND allow the request to proceed

### Requirement: Error Handling
The system SHALL provide consistent error responses across all endpoints.

#### Scenario: Validation error
- GIVEN a request contains invalid data
- WHEN the request is processed
- THEN the system SHALL return HTTP 422 Unprocessable Entity
- AND include detailed validation errors

#### Scenario: Internal server error
- GIVEN an unexpected error occurs during processing
- WHEN the request is handled
- THEN the system SHALL return HTTP 500 Internal Server Error
- AND log the error for debugging
- AND NOT expose internal implementation details
