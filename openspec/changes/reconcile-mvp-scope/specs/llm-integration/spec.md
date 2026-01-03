# Delta for LLM Integration Specification - MVP Scope Reconciliation

## MODIFIED Requirements

### Requirement: LLM Provider Integration

**Status:** ✅ IMPLEMENTED (Simplified)

**Original Spec:** Use aisuite for unified LLM interface with multiple providers.

**MVP Implementation:** Use OpenAI directly via Haystack's built-in `OpenAIGenerator` component.

#### Rationale for Divergence

1. **Haystack Integration:** Haystack 2.x has excellent native OpenAI support
2. **Reduced Complexity:** aisuite adds abstraction layer without immediate benefit
3. **Development Speed:** Direct OpenAI allows faster iteration
4. **Future Flexibility:** aisuite can be added in Phase 3 when multi-provider is needed

#### Scenario: Generate answer with OpenAI ✅ IMPLEMENTED

- GIVEN a query and retrieved context
- WHEN the LLM component generates an answer
- THEN the system SHALL use OpenAI's API (gpt-4o-mini by default)
- AND return the generated answer
- AND include usage metadata

---

### Requirement: Provider Selection

**Status:** ⏳ DEFERRED TO PHASE 3

The system SHALL support multiple LLM providers via aisuite.

> **MVP Note:** MVP uses OpenAI only. Multi-provider support (Groq, Anthropic) planned for Phase 3 when aisuite is integrated.

**Original Providers:**

- Groq (Llama 3.3 70B) - Primary (free, fast)
- OpenAI GPT-4o-mini - Fallback (cost-effective)
- Anthropic Claude 3.5 Sonnet - Premium

**MVP Provider:**

- OpenAI GPT-4o-mini - Single provider for simplicity

---

### Requirement: Provider Fallback

**Status:** ⏳ DEFERRED TO PHASE 3

The system SHALL fall back to alternative providers on failure.

> **MVP Note:** No fallback mechanism. Single provider (OpenAI) with basic error handling.

---

### Requirement: Streaming Responses

**Status:** ⏳ DEFERRED TO PHASE 2

The system SHALL support streaming token-by-token responses.

> **MVP Note:** All responses are synchronous. Streaming requires frontend SSE support.

---

### Requirement: Rate Limiting and Retry

**Status:** ⏳ DEFERRED TO PHASE 2

The system SHALL implement exponential backoff for rate limits.

> **MVP Note:** No retry logic implemented. Errors propagate to caller.

---

## ADDED Requirements (MVP Enhancements)

### Requirement: Embedder Caching

**Status:** ✅ IMPLEMENTED

The system SHALL cache the OpenAI embedder instance for performance.

#### Scenario: Reuse embedder across queries

- GIVEN multiple queries are processed
- WHEN embedding queries
- THEN the system SHALL reuse a single cached OpenAITextEmbedder instance
- AND reduce initialization overhead by ~90%

> **MVP Note:** This performance optimization was added during code review.
