# Troubleshooting Guide

This guide helps diagnose and resolve common issues with Quilora AI.

## Table of Contents
1. [Server Won't Start](#server-wont-start)
2. [Qdrant Connection Issues](#qdrant-connection-issues)
3. [OpenAI API Errors](#openai-api-errors)
4. [Slow Performance](#slow-performance)
5. [Empty Search Results](#empty-search-results)
6. [Streaming Issues](#streaming-issues)
7. [Docker Issues](#docker-issues)
8. [Testing Issues](#testing-issues)

---

## Server Won't Start

### Symptom
```
ModuleNotFoundError: No module named 'xyz'
```

**Solution**:
```bash
# Reinstall dependencies
uv sync

# Or with pip
pip install -r requirements.txt
```

### Symptom
```
Address already in use: Port 8000
```

**Solution**:
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn src.api.main:app --port 8001
```

### Symptom
```
OPENAI_API_KEY not set
```

**Solution**:
1. Create `.env` file in project root
2. Add: `OPENAI_API_KEY=sk-...`
3. Verify: `cat .env | grep OPENAI`

---

## Qdrant Connection Issues

### Symptom
```
ConnectionError: Cannot connect to Qdrant at http://localhost:6333
```

**Diagnosis**:
```bash
# Check if Qdrant is running
curl http://localhost:6333/healthz

# Expected: {"title":"qdrant - vector search engine","version":"..."}
```

**Solution 1: Start Qdrant**
```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  --name qdrant \
  qdrant/qdrant
```

**Solution 2: Use Docker Compose**
```bash
docker compose up -d qdrant
```

**Solution 3: Update QDRANT_URL in .env**
```
QDRANT_URL=http://localhost:6333  # Local
# or
QDRANT_URL=http://qdrant:6333     # Docker Compose
```

### Symptom
```
Collection 'documents' not found
```

**Solution**:
The collection is created automatically on first document upload. If you need to recreate:
```bash
# Delete collection via API
curl -X DELETE http://localhost:6333/collections/documents

# Or restart Qdrant (WARNING: deletes all data)
docker rm -f qdrant
docker run ...
```

---

## OpenAI API Errors

### Symptom
```
401 Unauthorized: Invalid API Key
```

**Solution**:
1. Verify API key is correct: https://platform.openai.com/api-keys
2. Check `.env` file has no extra spaces:
   ```
   OPENAI_API_KEY=sk-proj-...  # ✓ Correct
   OPENAI_API_KEY = sk-proj-...  # ✗ Wrong (spaces)
   ```
3. Restart server after updating `.env`

### Symptom
```
429 Rate Limit Exceeded
```

**Solution**:
- Check your OpenAI usage: https://platform.openai.com/usage
- Upgrade to paid tier if on free tier
- Implement request queueing (Phase 3)
- Our retry logic will handle transient rate limits

### Symptom
```
Timeout: OpenAI request timed out after 60s
```

**Diagnosis**:
- Check OpenAI status: https://status.openai.com/
- Review logs for retry attempts:
  ```bash
  docker logs quilora-ai-api-1 | grep "retry"
  ```

**Solution**:
- Wait for OpenAI service restoration
- Reduce `LLM_MAX_TOKENS` in `.env` to speed up generation
- Our retry logic (3 attempts with exponential backoff) should handle transient issues

---

## Slow Performance

### Symptom: Embedding takes >1s

**Diagnosis**:
```bash
# Check logs for timing
docker logs quilora-ai-api-1 | grep "embedding_ms"
```

**Solution**:
- Verify OpenAI API is healthy
- Check network latency: `ping api.openai.com`
- Consider caching embeddings for repeated queries (future work)

### Symptom: Search takes >500ms

**Diagnosis**:
```bash
# Check Qdrant performance
curl http://localhost:6333/collections/documents

# Look at "points_count" - high counts slow search
```

**Solution**:
- Increase `min_similarity_score` in `.env` (default 0.7)
- Reduce `retrieval_top_k` (default 5)
- Optimize Qdrant config (advanced)

### Symptom: Generation takes >30s

**Solution**:
- Reduce `LLM_MAX_TOKENS` in `.env` (default 1024)
- Use streaming mode for better UX: `?stream=true`
- Check OpenAI model status

---

## Empty Search Results

### Symptom
```json
{
  "documents": [],
  "answer": "I don't have enough information..."
}
```

**Diagnosis**:
1. Check if documents exist:
   ```bash
   curl http://localhost:8000/documents
   ```
2. Check similarity threshold:
   ```bash
   # In .env
   echo $MIN_SIMILARITY_SCORE  # Default 0.7
   ```
3. Review query and document content relevance

**Solution**:
1. Lower similarity threshold:
   ```
   MIN_SIMILARITY_SCORE=0.5  # In .env
   ```
2. Upload more relevant documents
3. Improve document metadata for filtering
4. Test with example query matching uploaded content

---

## Streaming Issues

### Symptom: Streaming not working, getting full response

**Diagnosis**:
```bash
# Check request includes stream parameter
curl -N http://localhost:8000/query?stream=true \
  -H "Content-Type: application/json" \
  -d '{"question":"What is RAG?"}'
```

**Expected Output**:
```
data: {"type":"documents",...}

data: {"type":"token","data":"RAG"}

data: {"type":"token","data":" is"}

data: {"type":"done",...}
```

**Solution**:
- Ensure `stream=true` query parameter
- Use `-N` flag with curl (no buffering)
- In browser, use EventSource API:
  ```javascript
  const es = new EventSource('/query?stream=true&question=...');
  es.onmessage = (e) => console.log(JSON.parse(e.data));
  ```

### Symptom: Stream hangs or times out

**Diagnosis**:
```bash
# Check server logs for errors
docker logs -f quilora-ai-api-1
```

**Solution**:
- Verify OpenAI API is responding
- Check for exceptions in logs
- Reduce `LLM_MAX_TOKENS` to speed up generation

---

## Docker Issues

### Symptom: Container exits immediately

**Diagnosis**:
```bash
docker logs quilora-ai-api-1
```

**Common Causes**:
1. Missing environment variables
2. Build errors
3. Port conflicts

**Solution**:
```bash
# Rebuild with no cache
docker compose build --no-cache

# Check docker-compose.yml environment section
# Ensure .env file exists with required vars
```

### Symptom: `docker compose up` fails

**Diagnosis**:
```bash
docker compose config  # Validate syntax
docker compose ps      # Check container status
```

**Solution**:
```bash
# Clean up and restart
docker compose down -v
docker compose up --build
```

### Symptom: Health check failing

**Diagnosis**:
```bash
# Check health status
docker compose ps

# View health check logs
docker inspect quilora-ai-api-1 | grep -A 10 Health
```

**Solution**:
- Ensure Qdrant is running first (depends_on)
- Check `/health` endpoint manually:
  ```bash
  docker exec quilora-ai-api-1 curl http://localhost:8000/health
  ```
- Verify `QDRANT_URL` in docker-compose.yml

---

## Testing Issues

### Symptom: Tests failing with "Qdrant connection refused"

**Solution**:
```bash
# Start Qdrant for tests
docker run -d -p 6333:6333 qdrant/qdrant

# Run tests
uv run pytest

# Or use docker compose
docker compose up -d qdrant
uv run pytest
```

### Symptom: "OpenAI API key not set" in tests

**Solution**:
1. Create `.env.test` with test API key
2. Or set environment variable:
   ```bash
   export OPENAI_API_KEY=sk-...
   uv run pytest
   ```

### Symptom: Import errors in tests

**Solution**:
```bash
# Ensure package is installed in editable mode
uv pip install -e .

# Or reinstall dependencies
uv sync
```

---

## Getting Help

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=DEBUG

# Restart server
docker compose restart api
```

### Check Logs

```bash
# API logs
docker logs -f quilora-ai-api-1

# Qdrant logs
docker logs -f quilora-ai-qdrant-1

# Filter for errors
docker logs quilora-ai-api-1 2>&1 | grep ERROR
```

### Health Check

```bash
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "qdrant_connected": true,
#   "uptime": 123.45,
#   "api_version": "0.3.0"
# }
```

### GitHub Issues

If none of these solutions work:
1. Gather logs: `docker logs quilora-ai-api-1 > error.log`
2. Note your environment:
   - OS and version
   - Docker version
   - Python version
3. Open issue: https://github.com/yourusername/quilora-ai/issues

### Quick Diagnosis Script

```bash
#!/bin/bash
echo "=== Quilora AI Diagnostics ==="
echo "1. Checking Python environment..."
python --version
which python

echo "2. Checking Qdrant..."
curl -s http://localhost:6333/healthz || echo "Qdrant not running"

echo "3. Checking API..."
curl -s http://localhost:8000/health || echo "API not running"

echo "4. Checking OpenAI API key..."
[ -z "$OPENAI_API_KEY" ] && echo "OPENAI_API_KEY not set" || echo "OPENAI_API_KEY is set"

echo "5. Checking Docker containers..."
docker ps | grep quilora

echo "=== End Diagnostics ==="
```

Save as `diagnose.sh`, run with `bash diagnose.sh`.
