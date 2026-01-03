# Implementation Tasks: Add Multi-LLM Support

## Status
- **Phase**: Phase 3
- **Status**: Not Started
- **Priority**: High
- **Estimated Effort**: 4-6 hours

## Prerequisites
- [ ] Review aisuite documentation: https://github.com/andrewyng/aisuite
- [ ] Confirm all API keys available (OpenAI, Anthropic, Groq)
- [ ] Review Phase 2 retry/timeout logic for compatibility
- [ ] Archive Phase 2 changes if not already done

## 1. Setup and Dependencies
- [ ] Add `aisuite>=0.1.3` to requirements.txt
- [ ] Install aisuite: `uv pip install aisuite`
- [ ] Verify aisuite imports work
- [ ] Create `src/llm/` package directory
- [ ] Create `src/llm/__init__.py`

## 2. Provider Registry Implementation
- [ ] Create `src/llm/provider.py`
- [ ] Implement `LLMProviderRegistry` class
- [ ] Add method to initialize aisuite clients for all providers
- [ ] Implement provider health check method
- [ ] Add method to get available providers list
- [ ] Handle API key validation and missing keys gracefully
- [ ] Add logging for provider initialization
- [ ] Write unit tests for provider registry (5+ scenarios)

## 3. Query Complexity Classifier
- [ ] Create `src/llm/classifier.py`
- [ ] Implement `QueryComplexityClassifier` class
- [ ] Add word count analysis
- [ ] Add keyword detection (technical terms, reasoning indicators)
- [ ] Add multi-question detection
- [ ] Implement classification logic (simple/moderate/complex)
- [ ] Return confidence scores with classifications
- [ ] Write unit tests for classifier (10+ test cases)

## 4. Provider Router
- [ ] Create `src/llm/router.py`
- [ ] Implement `ProviderRouter` class
- [ ] Add strategy-based routing (speed/balanced/quality)
- [ ] Implement complexity-based provider selection
- [ ] Add fallback chain logic
- [ ] Implement provider override handling
- [ ] Add circuit breaker pattern for failing providers
- [ ] Log routing decisions with reasoning
- [ ] Write unit tests for router (15+ scenarios)

## 5. Configuration Updates
- [ ] Update `src/config/settings.py`
- [ ] Add `llm_provider_strategy: str` (speed/balanced/quality)
- [ ] Add `llm_complexity_simple_max_words: int` (default 50)
- [ ] Add `llm_complexity_moderate_max_words: int` (default 200)
- [ ] Add `llm_enable_provider_override: bool` (default True)
- [ ] Add `llm_circuit_breaker_threshold: int` (default 5)
- [ ] Update `.env.example` with new variables
- [ ] Document configuration options in README

## 6. Pipeline Integration
- [ ] Update `src/pipelines/retrieval.py`
- [ ] Replace OpenAI imports with aisuite
- [ ] Add complexity classification step
- [ ] Add provider selection step
- [ ] Modify `retrieve_documents()` to use aisuite
- [ ] Update retry logic to handle provider fallback
- [ ] Add provider metadata to response
- [ ] Modify `retrieve_documents_streaming()` to use aisuite
- [ ] Handle streaming differences across providers
- [ ] Preserve SSE format from Phase 2
- [ ] Add provider information to streaming metadata

## 7. API Schema Updates
- [ ] Update `src/api/schemas/query.py`
- [ ] Add optional `provider: str` field to QueryRequest
- [ ] Add validator for provider field (openai|anthropic|groq|null)
- [ ] Update response metadata to include `provider_used: str`
- [ ] Update response metadata to include `provider_fallback: bool`
- [ ] Update API documentation/docstrings

## 8. Health Endpoint Enhancement
- [ ] Update `src/api/routes/health.py`
- [ ] Add provider status to health check response
- [ ] Show available providers list
- [ ] Show provider error rates (if >0)
- [ ] Add last successful request timestamp per provider
- [ ] Test health endpoint with multiple providers

## 9. Testing
- [ ] Write `tests/test_llm_provider.py` (provider registry tests)
- [ ] Write `tests/test_llm_classifier.py` (classifier tests)
- [ ] Write `tests/test_llm_router.py` (router tests)
- [ ] Update `tests/test_pipelines.py` (test with all providers)
- [ ] Add integration tests for provider fallback
- [ ] Add integration tests for streaming with each provider
- [ ] Test provider override functionality
- [ ] Test with missing API keys (graceful degradation)
- [ ] Test circuit breaker behavior
- [ ] Ensure all existing tests still pass (29 tests)
- [ ] Aim for 80%+ code coverage on new code

## 10. Documentation
- [ ] Update `docs/architecture.md`
- [ ] Add multi-LLM architecture diagram
- [ ] Document provider selection logic
- [ ] Update `docs/troubleshooting.md`
- [ ] Add provider-specific troubleshooting
- [ ] Add aisuite debugging tips
- [ ] Update README.md
- [ ] Document provider configuration
- [ ] Add provider override examples
- [ ] Update API examples with provider metadata
- [ ] Create `docs/PHASE3_COMPLETION.md` (after all tasks done)

## 11. Performance Validation
- [ ] Benchmark query time with each provider
- [ ] Verify fallback doesn't add excessive latency
- [ ] Test streaming latency across providers
- [ ] Validate complexity classifier accuracy (>80% on sample set)
- [ ] Measure cost savings with smart routing

## 12. Final Validation
- [ ] Run full test suite: `uv run pytest`
- [ ] Verify all 29+ existing tests pass
- [ ] Run with all providers enabled
- [ ] Run with only OpenAI (graceful degradation test)
- [ ] Test Docker Compose deployment
- [ ] Verify health endpoint shows provider status
- [ ] Test streaming with curl for all providers
- [ ] Run linting: `uv run black . && uv run isort . && uv run ruff check .`
- [ ] Check for any security issues (API key exposure)
- [ ] Validate OpenSpec: `openspec validate add-multi-llm-support --strict`

## Post-Implementation
- [ ] Update docker-compose.yml if needed
- [ ] Update CI/CD workflows if needed
- [ ] Create git commit with detailed message
- [ ] Archive this change proposal
- [ ] Update main specs if capabilities evolved

## Notes
- Maintain backward compatibility - existing deployments should work without changes
- Provider override is optional feature for testing/debugging
- Complexity classifier can start simple and improve iteratively
- Circuit breaker prevents cascading failures
- All provider operations should have timeouts (60s from Phase 2)

## Blockers
None identified. All dependencies available.

## Success Metrics
- All tests passing (target: 44+ tests, 29 existing + 15 new)
- Cost reduction: 30-50% through smart routing
- No API breaking changes
- Streaming works across all providers
- Fallback time <500ms additional latency
- Provider selection accuracy >80%
