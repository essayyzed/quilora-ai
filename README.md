# Quilora

> Ask your documents anything

**Quilora** is an intelligent document assistant powered by Retrieval-Augmented Generation (RAG). Built with Haystack 2.x, it combines the speed and cost-efficiency of Small Language Models (Groq/Llama 3.3) with the flexibility to scale to frontier models (GPT-4, Claude) when needed.

Query your documents in natural language and get accurate, context-aware answers in real-time.

## ✨ Features

- **📄 Document Management** - Upload, list, and delete documents via REST API
- **🔍 RAG-Powered Search** - Semantic search with AI-generated answers
- **🌊 Streaming Responses** - Real-time token streaming via Server-Sent Events (SSE)
- **🔄 Automatic Retries** - Exponential backoff for OpenAI and Qdrant failures
- **⏱️ Performance Tracking** - Detailed timing metrics for embedding, search, and generation
- **🐳 Docker Ready** - Full containerization with docker-compose orchestration
- **📊 Observability** - Request tracking, structured logging, health checks with uptime
- **🔒 Production Ready** - Timeouts, error handling, non-root containers, CI/CD
- **⚡ Fast** - Optimized with connection pooling and singleton patterns
- **📖 Documentation** - Comprehensive architecture diagram and troubleshooting guide

## Project Structure

```
quilora-ai
├── src
│   ├── api                # FastAPI application and routes
│   ├── pipelines          # Logic for indexing and retrieval
│   ├── components         # Custom components for Haystack
│   ├── document_stores    # Document storage implementation
│   └── config             # Configuration settings
├── data
│   └── documents          # Directory for documents
├── tests                  # Unit tests for the application
├── .env.example           # Example environment variables
├── requirements.txt       # Project dependencies
└── pyproject.toml         # Project metadata and configuration
```

## Prerequisites

Before setting up Quilora, ensure you have the following installed:

- **Python 3.11+** - Required for running the application
- **Docker** - Required for running Qdrant vector database
- **uv** - Fast Python package installer (install from https://docs.astral.sh/uv/)

## 📚 Documentation

- **[Architecture Overview](docs/architecture.md)** - System design, components, and data flow
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[OpenSpec Change Proposals](openspec/changes/)** - Detailed change history

### API Keys

You'll need the following API keys:

- **OpenAI** (Required) - Used for document embeddings and fallback LLM
  - Get your key: https://platform.openai.com/api-keys
- **Groq** (Required) - Primary LLM provider (free tier available)
  - Get your key: https://console.groq.com
- **Anthropic** (Optional) - Premium LLM for complex queries
  - Get your key: https://console.anthropic.com

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd quilora-ai
   ```

2. **Set up environment variables:**

   ```bash
   # Copy the example environment file
   cp .env.example .env
   ```

   **Important:** If `.env.example` is missing, create `.env` manually with the required keys:

   ```bash
   # Required API keys
   OPENAI_API_KEY=your_openai_key_here
   GROQ_API_KEY=your_groq_key_here

   # Optional API keys
   ANTHROPIC_API_KEY=your_anthropic_key_here

   # Qdrant configuration
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   ```

   Then edit `.env` and replace the placeholder values with your actual API keys.

   **Security Warning:**

   - NEVER commit `.env` to version control - it contains secrets!
   - Ensure `.env` is in your `.gitignore` file
   - If you accidentally committed secrets, rotate your API keys immediately

   To verify `.env` is ignored by git:

   ```bash
   # Check if .env is in .gitignore
   grep -q "^\.env$" .gitignore && echo "✓ .env is ignored" || echo "⚠ Add .env to .gitignore!"
   ```

3. **Install dependencies:**

   ```bash
   uv sync
   ```

4. **Start Qdrant (required for vector storage):**

   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

5. **Run the application:**

   **Option A: Local Development**

   ```bash
   .venv/bin/python3 -m uvicorn src.api.main:app --reload
   ```

   **Option B: Docker Compose (Recommended)**

   ```bash
   🧪 Testing
   ```

Run all tests:

```bash
uv run pytest -v
```

Run with coverage:

```bash
uv run pytest --cov=src --cov-report=term
```

Run only integration tests (requires Qdrant):

```bash
uv run pytest -m integration
```

## 🐳 Docker Deployment

The project includes full Docker support for production deployment:

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild after code changes
docker compose up --build
```

Services:

- **API**: http://localhost:8000
- **Qdrant**: http://localhost:6333

## 📊 Monitoring

The application includes structured logging with request tracking:

- **Request IDs**: Every request gets a unique ID (available in `X-Request-ID` header)
- **Performance Metrics**: Automatic timing for embeddings, retrieval, and generation
- **Health Checks**: `/health` endpoint monitors Qdrant connectivity

Configure logging level:

```bash
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🔧 Development

### Code Quality

Format code:

```bash
uv run black src/ tests/
uv run isort src/ tests/
```

Lint code:

```bash
uv run ruff check src/ tests/
```

### CI/CD

The project uses GitHub Actions for:

- **Automated Testing**: Runs on every push and PR
- **Linting**: Black, isort, ruff checks
- **Coverage Reporting**: Uploads to Codecov

### Health & Status

- `GET /health` - Health check with Qdrant connectivity status

### Document Management

- `POST /documents` - Upload document from JSON content
- `POST /documents/upload` - Upload document file (TXT, MD)
- `GET /documents` - List all documents (paginated)
- `DELETE /documents/{id}` - Delete specific document
- `DELETE /documents?all=true` - Delete all documents

### Query & RAG

- `POST /query` - Query documents with AI-generated answers
  - `stream=false` (default): Complete JSON response
  - `stream=true`: Server-Sent Events streaming

### Example: Streaming Query

```bash
curl -N -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAG?",
    "stream": true
  }'
```

### Example: Upload Document

```bash
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "content": "RAG combines retrieval and generation for better AI answers.",
    "metadata": {"source": "tutorial", "author": "team"}
  }'
```

## Usage

Once the application is running, you can access the API at `http://localhost:8000`. Use the `/docs` endpoint to view the interactive API documentation.

## Testing

To run the tests, use the following command:

```
pytest
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
