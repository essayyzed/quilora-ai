# Proposal: Add Multi-LLM Support via Aisuite

## Overview
Implement flexible multi-LLM provider support using aisuite library, enabling Quilora to intelligently route requests across multiple LLM providers (OpenAI, Anthropic, Groq) based on query complexity, cost, and availability. This fulfills the original architecture vision of hybrid SLM/frontier model usage.

## Motivation
The current implementation uses OpenAI directly for both embeddings and generation. While functional, this:
- Creates vendor lock-in
- Limits cost optimization opportunities
- Prevents leveraging provider-specific strengths
- Doesn't fulfill the original tiered LLM strategy (Groq for speed, OpenAI for balance, Anthropic for quality)

**Original Vision (from MVP spec):**
- **Primary**: Groq/Llama 3.3 70B (free, fast) - 80% of queries
- **Fallback**: OpenAI/GPT-4o-mini (low cost, reliable) - 15% of queries
- **Premium**: Anthropic/Claude 3.5 Sonnet (highest quality) - 5% of queries

## Goals
1. **Aisuite Integration**: Replace direct OpenAI SDK calls with aisuite abstraction layer
2. **Multi-Provider Support**: Enable OpenAI, Anthropic, and Groq providers
3. **Smart Routing**: Implement provider selection logic based on query complexity
4. **Graceful Fallback**: Automatic failover between providers
5. **Streaming Support**: Maintain streaming functionality across all providers
6. **Configuration**: Provider preferences and API keys via environment variables
7. **Backward Compatibility**: Existing API behavior unchanged

## What Changes

### LLM Integration (`llm-integration` capability)
- **ADDED**: Aisuite adapter for multi-provider LLM support
- **ADDED**: Provider registry with OpenAI, Anthropic, Groq clients
- **ADDED**: Query complexity classifier (simple/moderate/complex)
- **ADDED**: Provider selection logic based on complexity and availability
- **ADDED**: Unified streaming interface across providers
- **MODIFIED**: Error handling to support multi-provider fallback

### Pipelines (`pipelines` capability)
- **MODIFIED**: `retrieve_documents()` to use aisuite instead of direct OpenAI
- **MODIFIED**: `retrieve_documents_streaming()` to use aisuite streaming
- **ADDED**: Complexity detection for routing decisions
- **ADDED**: Provider fallback chain (primary → fallback → premium)

### Configuration
- **ADDED**: `LLM_PROVIDER_STRATEGY` - "speed"|"balanced"|"quality"
- **ADDED**: `LLM_COMPLEXITY_THRESHOLD` - classifier threshold settings
- **MODIFIED**: Provider settings now support aisuite format

## Non-Goals
- Fine-tuning models
- Custom model deployment
- Advanced prompt engineering framework
- Query cost tracking/budgets (future enhancement)
- Real-time provider selection based on latency (future)

## Success Criteria
- [x] Aisuite successfully integrated and tested
- [x] All three providers (OpenAI, Anthropic, Groq) operational
- [x] Query complexity classifier achieves >80% accuracy on test set
- [x] Automatic failover works when primary provider fails
- [x] Streaming works across all providers
- [x] No breaking changes to existing API contracts
- [x] Response quality maintained or improved vs Phase 2
- [x] Average query cost reduced by 30-50% using smart routing
- [x] All existing tests pass plus 15+ new provider tests

## Impact Assessment

### Affected Capabilities
- `llm-integration` - Major changes, new aisuite layer
- `pipelines` - Moderate changes, swap OpenAI SDK for aisuite

### Code Impact
**New Files:**
- `src/llm/provider.py` - Aisuite provider registry and configuration
- `src/llm/classifier.py` - Query complexity classifier
- `src/llm/router.py` - Provider selection and fallback logic
- `src/llm/__init__.py` - Module initialization
- `tests/test_llm_provider.py` - Provider tests
- `tests/test_llm_classifier.py` - Classifier tests
- `tests/test_llm_router.py` - Router tests

**Modified Files:**
- `src/pipelines/retrieval.py` - Replace OpenAI calls with aisuite
- `src/config/settings.py` - Add aisuite configuration
- `requirements.txt` - Add aisuite>=0.1.3

**Configuration:**
```env
# Provider Strategy
LLM_PROVIDER_STRATEGY=balanced  # speed|balanced|quality

# Provider-specific settings (aisuite format)
PRIMARY_LLM_PROVIDER=groq:llama-3.3-70b-versatile
FALLBACK_LLM_PROVIDER=openai:gpt-4o-mini
PREMIUM_LLM_PROVIDER=anthropic:claude-3-5-sonnet-20240620

# Complexity thresholds
LLM_COMPLEXITY_SIMPLE_MAX_WORDS=50
LLM_COMPLEXITY_MODERATE_MAX_WORDS=200
```

### Breaking Changes
**None** - API contracts remain unchanged. Internal provider switching is transparent.

### Migration Path
Existing deployments:
1. Update `requirements.txt` and install aisuite
2. Add new environment variables (providers default to existing values)
3. Restart API service
4. Verify health check shows multiple providers available

Optional:
- Set `LLM_PROVIDER_STRATEGY` to optimize for speed or quality
- Configure complexity thresholds for custom routing

## Dependencies
- **aisuite>=0.1.3** - Multi-LLM abstraction library
- Existing OpenAI, Anthropic, Groq API keys
- Compatible with Haystack 2.x (adapter layer bridges them)

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Aisuite API changes | High | Medium | Pin specific version, create abstraction layer |
| Provider-specific streaming differences | Medium | High | Normalize streaming interface in adapter |
| Increased complexity in error handling | Medium | Medium | Comprehensive fallback logic with circuit breakers |
| Cost tracking across providers | Low | Low | Future enhancement, log provider usage |
| Classifier accuracy | Medium | Medium | Start with simple heuristics, improve iteratively |

## Timeline
**Estimated effort**: 4-6 hours
1. Aisuite integration (2h)
2. Classifier implementation (1h)
3. Router and fallback logic (1h)
4. Testing and validation (2h)

## Open Questions
1. Should we implement request-level provider override (e.g., `?provider=anthropic`)?
   - **Decision**: Yes, add optional `provider` parameter to QueryRequest
2. How to handle embeddings? Keep OpenAI or add multi-provider?
   - **Decision**: Keep OpenAI for embeddings (Phase 3), multi-provider embeddings in Phase 4
3. Logging provider selection decisions?
   - **Decision**: Yes, log provider used in structured logs with reasoning

## Approval
- [ ] Technical review
- [ ] Architecture approval
- [ ] Security review (API key management)
- [ ] Go/No-Go decision
