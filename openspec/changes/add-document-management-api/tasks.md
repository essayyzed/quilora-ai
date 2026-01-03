# Implementation Tasks - Document Management API (Phase 1.5)

## 1. Schemas

- [x] 1.1 Create `src/api/schemas/documents.py` with Pydantic models
- [x] 1.2 Define `DocumentCreateRequest` (content, metadata)
- [x] 1.3 Define `DocumentResponse` (id, metadata, content_preview, chunk_count)
- [x] 1.4 Define `DocumentListResponse` (documents, total_count)
- [x] 1.5 Define `HealthResponse` (status, qdrant, timestamp)

## 2. Health Endpoint

- [x] 2.1 Create `src/api/routes/health.py`
- [x] 2.2 Implement GET /health with Qdrant connectivity check
- [x] 2.3 Return proper status codes (200 healthy, 503 unhealthy)
- [x] 2.4 Register health router in main.py

## 3. Document Endpoints

- [x] 3.1 Create `src/api/routes/documents.py`
- [x] 3.2 Implement POST /documents for JSON content upload
- [x] 3.3 Implement POST /documents/upload for file upload (multipart)
- [x] 3.4 Implement GET /documents with pagination (limit, offset)
- [x] 3.5 Implement DELETE /documents/{document_id}
- [x] 3.6 Implement DELETE /documents?all=true for bulk deletion
- [x] 3.7 Register documents router in main.py

## 4. Integration with Pipelines

- [x] 4.1 Connect document upload to indexing pipeline
- [x] 4.2 Add file content extraction (txt, md)
- [x] 4.3 Handle indexing errors gracefully

## 5. Testing

- [x] 5.1 Add tests for health endpoint (healthy, unhealthy scenarios)
- [x] 5.2 Add tests for document upload (success, validation errors)
- [x] 5.3 Add tests for document listing (with data, empty, pagination)
- [x] 5.4 Add tests for document deletion (exists, not found, bulk)

## 6. Documentation

- [x] 6.1 Verify OpenAPI docs are auto-generated correctly
- [ ] 6.2 Update README with new endpoints
- [ ] 6.3 Update tasks.md in implement-rag-application (mark Phase 1.5 complete)
