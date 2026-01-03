# Delta for Pipelines Specification - MVP Scope Reconciliation

## MODIFIED Requirements

### Requirement: Indexing Pipeline

**Status:** ✅ IMPLEMENTED

The system SHALL provide a pipeline to process and index documents into the vector store.

#### Scenario: Index documents with embeddings ✅ IMPLEMENTED

- GIVEN a list of Haystack Document objects
- WHEN the indexing pipeline processes the documents
- THEN the system SHALL split documents into chunks (configurable size/overlap)
- AND generate embeddings using OpenAIDocumentEmbedder
- AND store chunks in Qdrant with metadata
- AND return pipeline results

> **MVP Note:** File reading (PDF, DOCX) must be done before calling pipeline. Documents must be passed as Haystack Document objects.

---

### Requirement: Retrieval Pipeline

**Status:** ✅ IMPLEMENTED (Non-Streaming)

The system SHALL provide a pipeline to retrieve relevant context and generate answers.

#### Scenario: Answer question with context ✅ IMPLEMENTED

- GIVEN a user query
- WHEN the retrieval pipeline executes
- THEN the system SHALL embed the query using cached OpenAITextEmbedder
- AND retrieve top-k most relevant chunks from Qdrant
- AND build a prompt with retrieved context
- AND generate an answer using OpenAIGenerator
- AND return answer, documents, and metadata

#### Scenario: Streaming response ⏳ DEFERRED TO PHASE 2

- GIVEN a user requests streaming output
- WHEN the retrieval pipeline generates an answer
- THEN the system SHALL stream tokens via SSE

> **MVP Note:** Streaming not implemented. All responses are complete JSON.

---

### Requirement: Pipeline Error Recovery

**Status:** ⏳ PARTIAL (PHASE 2 for full implementation)

#### Scenario: Basic error handling ✅ IMPLEMENTED

- GIVEN an error occurs during pipeline execution
- WHEN the error is caught
- THEN the system SHALL log the error internally
- AND return a generic error message to caller

#### Scenario: Retry with exponential backoff ⏳ DEFERRED TO PHASE 2

- GIVEN a transient failure (rate limit, connection timeout)
- WHEN the pipeline encounters the error
- THEN the system SHALL retry with exponential backoff

> **MVP Note:** No retry logic. Errors fail immediately.

---

### Requirement: Context Window Management

**Status:** ⏳ DEFERRED TO PHASE 2

The system SHALL manage token limits for different LLM providers.

> **MVP Note:** No token truncation logic. Relies on reasonable chunk sizes and top_k limits.

---

## ADDED Requirements (MVP Enhancements)

### Requirement: Document Store Caching

**Status:** ✅ IMPLEMENTED

The system SHALL cache the document store instance for performance.

#### Scenario: Reuse document store connection

- GIVEN multiple queries are processed
- WHEN accessing Qdrant
- THEN the system SHALL reuse a single cached QdrantDocumentStore instance
- AND reduce connection overhead

### Requirement: Thread-Safe Singleton

**Status:** ✅ IMPLEMENTED

The system SHALL provide thread-safe access to shared resources.

#### Scenario: Concurrent query handling

- GIVEN multiple concurrent queries
- WHEN initializing shared resources (embedder, document store)
- THEN the system SHALL use double-checked locking pattern
- AND prevent race conditions

> **MVP Note:** Added during code review for production readiness.
