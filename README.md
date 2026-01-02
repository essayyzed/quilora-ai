# Quilora

> Ask your documents anything

**Quilora** is an intelligent document assistant powered by Retrieval-Augmented Generation (RAG). Built with Haystack 2.x, it combines the speed and cost-efficiency of Small Language Models (Groq/Llama 3.3) with the flexibility to scale to frontier models (GPT-4, Claude) when needed.

Query your documents in natural language and get accurate, context-aware answers in real-time.

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
   ```bash
   uv run uvicorn src.api.main:app --reload
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
