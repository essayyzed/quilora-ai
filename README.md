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

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd quilora-ai
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your actual API keys
   # NEVER commit .env - it contains secrets!
   ```
   
   Get your API keys:
   - Groq: https://console.groq.com (free)
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com (optional)

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