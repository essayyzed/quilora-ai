# Design Document: RAG Application Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Vue 3 Frontend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Chat View    │  │ Upload View  │  │ Documents    │  │
│  │ Component    │  │ Component    │  │ List         │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│           │               │                 │            │
│           └───────────────┴─────────────────┘            │
│                           │                              │
│                      API Service                         │
│                   (HTTP + SSE Client)                    │
└───────────────────────────┬─────────────────────────────┘
                            │ REST/SSE
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    FastAPI Backend                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Route Handlers                       │   │
│  │  /health  /documents  /query  /documents/{id}    │   │
│  └─────┬────────────────────┬───────────────────────┘   │
│        │                    │                            │
│  ┌─────▼────────┐    ┌──────▼──────┐                    │
│  │ Indexing     │    │ Retrieval   │                    │
│  │ Pipeline     │    │ Pipeline    │                    │
│  │              │    │             │                    │
│  │ ┌──────────┐ │    │ ┌─────────┐│                    │
│  │ │File      │ │    │ │Query    ││                    │
│  │ │Reader    │ │    │ │Embedder ││                    │
│  │ └────┬─────┘ │    │ └────┬────┘│                    │
│  │      │       │    │      │     │                    │
│  │ ┌────▼─────┐ │    │ ┌────▼────┐│                    │
│  │ │Text      │ │    │ │Retriever││                    │
│  │ │Chunker   │ │    │ └────┬────┘│                    │
│  │ └────┬─────┘ │    │      │     │                    │
│  │      │       │    │ ┌────▼────┐│                    │
│  │ ┌────▼─────┐ │    │ │Prompt   ││                    │
│  │ │Embedder  │ │    │ │Builder  ││                    │
│  │ └────┬─────┘ │    │ └────┬────┘│                    │
│  │      │       │    │      │     │                    │
│  │ ┌────▼─────┐ │    │ ┌────▼────┐│                    │
│  │ │Writer to │ │    │ │aisuite  ││                    │
│  │ │Qdrant    │ │    │ │LLM Gen  ││                    │
│  │ └──────────┘ │    │ └─────────┘│                    │
│  └──────────────┘    └─────────────┘                    │
└─────────────┬────────────────┬──────────────────────────┘
              │                │
    ┌─────────▼────────┐  ┌────▼──────────────────┐
    │   Qdrant         │  │   aisuite             │
    │   Vector DB      │  │   (LLM Abstraction)   │
    │                  │  │                       │
    │ Collections:     │  │ Providers:            │
    │ - documents      │  │ - OpenAI              │
    │                  │  │ - Anthropic           │
    │ Embeddings:      │  │ - Google              │
    │ - 768/1536 dim   │  │ - AWS Bedrock         │
    └──────────────────┘  │ - Cohere, Mistral...  │
                          └───────────────────────┘
```

## Component Design

### 1. Document Store (Qdrant)
**Purpose**: Vector database for storing document embeddings and metadata

**Design Decisions**:
- Use single collection "documents" with metadata filtering
- Store document chunks with parent document ID for reconstruction
- Use cosine similarity for retrieval (standard for text embeddings)

**Key Methods**:
```python
class QdrantStore:
    def initialize_collection(collection_name: str, vector_dim: int)
    def upsert_documents(documents: List[Document])
    def search(query_vector: List[float], top_k: int) -> List[Document]
    def delete_document(doc_id: str)
```

### 2. LLM Integration (aisuite)
**Purpose**: Provider-agnostic LLM interface for answer generation

**Design Decisions**:
- **SLM-First Strategy**: Use Groq (Llama 3.3 70B) as primary - excellent quality for RAG at zero cost
- **Why SLMs work for RAG**: Context is provided, so model just synthesizes facts (plays to SLM strengths)
- **Automatic fallback**: Primary → Fallback → Premium (configurable per query)
- Create Haystack-compatible component wrapping aisuite.Client
- Support both streaming and non-streaming responses
- Token counting for cost tracking and provider selection optimization

**Key Interface**:
```python
class AISuiteLLMComponent:
    @component
    def run(self, prompt: str, stream: bool = False) -> Dict[str, Any]:
        # Returns {"replies": List[str]} or stream generator
```

**Provider Configuration** (Hybrid Strategy):
```python
# Tiered LLM approach for cost optimization
PRIMARY_LLM = "groq:llama-3.3-70b-versatile"  # Free, fast, good quality
FALLBACK_LLM = "openai:gpt-4o-mini"  # $0.15/1M tokens, reliable backup
PREMIUM_LLM = "anthropic:claude-3-5-sonnet-20240620"  # Best quality, for critical queries

# Auto-fallback logic:
# 1. Try PRIMARY_LLM (Groq) - covers 80% of queries
# 2. On failure/timeout → FALLBACK_LLM (GPT-4o-mini)
# 3. User can explicitly request PREMIUM_LLM
```

### 3. Indexing Pipeline
**Purpose**: Process documents and store them in Qdrant

**Pipeline Structure**:
```
FileReader → TextSplitter → Embedder → QdrantWriter
```

**Component Details**:
- **FileReader**: Supports PDF, TXT, MD, DOCX (using PyPDF2, python-docx)
- **TextSplitter**: Recursive chunking with configurable size (512 tokens) and overlap (50 tokens)
- **Embedder**: OpenAI text-embedding-3-small or sentence-transformers
- **QdrantWriter**: Batch upsert with metadata

### 4. Retrieval Pipeline
**Purpose**: Answer queries using retrieved context

**Pipeline Structure**:
```
QueryEmbedder → Retriever → PromptBuilder → AISuiteLLM
```

**Component Details**:
- **QueryEmbedder**: Same model as indexing embedder
- **Retriever**: Top-k similarity search (k=5 default)
- **PromptBuilder**: Template-based with system + user messages
- **AISuiteLLM**: Streaming response generator

**Prompt Template**:
```
System: You are a helpful assistant. Answer questions based on the provided context.

Context:
{retrieved_documents}

Question: {query}

Answer:
```

### 5. FastAPI Endpoints

#### POST /documents
**Purpose**: Upload and index documents
```python
Request: multipart/form-data with file
Response: {"document_id": str, "status": "indexed", "chunks": int}
```

#### GET /documents
**Purpose**: List all indexed documents
```python
Response: [{"id": str, "filename": str, "uploaded_at": datetime, "chunks": int}]
```

#### DELETE /documents/{id}
**Purpose**: Remove document from index
```python
Response: {"status": "deleted"}
```

#### POST /query
**Purpose**: Query documents with streaming response
```python
Request: {"query": str, "stream": bool, "provider": Optional[str]}
Response: SSE stream or JSON {"answer": str, "sources": List[str]}
```

#### GET /health
**Purpose**: Health check
```python
Response: {"status": "healthy", "qdrant": bool, "llm": bool}
```

### 6. Frontend Architecture

**Tech Stack**:
- Vue 3 Composition API
- TypeScript for type safety
- Vite for build tooling
- Pinia (optional) for state management

**Key Components**:

**ChatView.vue**:
```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp: Date;
}

// Manages chat history and query submission
```

**DocumentUpload.vue**:
```typescript
// File upload with progress tracking
// Drag-and-drop support
// Document list with delete functionality
```

**API Service**:
```typescript
class APIService {
  async uploadDocument(file: File): Promise<Document>
  async queryWithStream(query: string): AsyncGenerator<string>
  async listDocuments(): Promise<Document[]>
}
```

## Data Flow

### Document Indexing Flow
1. User uploads file via frontend
2. FastAPI receives file → saves temporarily
3. Indexing pipeline processes:
   - Read file content
   - Split into chunks
   - Generate embeddings
   - Store in Qdrant with metadata
4. Return document_id and status to frontend

### Query Flow
1. User types question in frontend
2. POST /query with stream=true
3. Backend:
   - Embed query
   - Retrieve top-k chunks from Qdrant
   - Build prompt with context
   - Stream LLM response via aisuite
4. Frontend receives SSE stream and displays incrementally

## Configuration

### Environment Variables
```bash
# LLM Configuration (Tiered Strategy)
GROQ_API_KEY=gsk_...  # Free tier available at https://console.groq.com
OPENAI_API_KEY=sk-...  # For fallback and embeddings
ANTHROPIC_API_KEY=sk-ant-...  # Optional, for premium queries

PRIMARY_LLM=groq:llama-3.3-70b-versatile
FALLBACK_LLM=openai:gpt-4o-mini
PREMIUM_LLM=anthropic:claude-3-5-sonnet-20240620

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# Document Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### Settings Class (Pydantic)
```python
class Settings(BaseSettings):
    openai_api_key: str
    anthropic_api_key: Optional[str]
    llm_provider: str = "openai:gpt-4o"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    # ... more settings
```

## Error Handling

### Backend
- **LLM Failures**: Retry with exponential backoff, fallback to alternative provider
- **Qdrant Failures**: Return 503 Service Unavailable
- **Invalid Files**: Return 400 Bad Request with error details
- **Rate Limiting**: Implement token bucket algorithm

### Frontend
- **Network Errors**: Show retry button
- **Streaming Interruptions**: Reconnect with exponential backoff
- **File Upload Failures**: Show error message with specific reason

## Security Considerations
- API keys stored in environment variables, never in code
- Input validation for file uploads (size, type)
- Rate limiting on query endpoint (10 requests/minute per IP)
- CORS configured for specific frontend origin
- No user data logging (privacy-first)

## Performance Optimization
- Connection pooling for Qdrant
- Async I/O throughout FastAPI
- Batch embedding generation where possible
- Caching for frequently asked questions (future)
- CDN for frontend assets (production)

## Scalability Path
1. **Current**: Single-instance deployment with Docker Compose
2. **Phase 2**: Horizontal scaling with load balancer
3. **Phase 3**: Separate embedding service
4. **Phase 4**: Distributed Qdrant cluster
