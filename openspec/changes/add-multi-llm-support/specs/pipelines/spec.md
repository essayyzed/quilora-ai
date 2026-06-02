# Pipelines Specification - Delta

## MODIFIED Requirements

### Requirement: Document Retrieval with Answer Generation

The system SHALL retrieve relevant documents from the vector store and generate accurate answers using multi-provider LLM support through aisuite, with intelligent provider selection based on query complexity and configured strategy.

**Modified behavior**: Uses aisuite for multi-provider LLM support instead of direct OpenAI SDK, enabling provider selection, fallback, and cost optimization.

#### Scenario: Generate answer with Groq (speed strategy)

- **GIVEN** a query "What is RAG?"
- **AND** query complexity is "simple"
- **AND** LLM_PROVIDER_STRATEGY is "speed"
- **WHEN** retrieve_documents() is called
- **THEN** documents SHALL be retrieved from Qdrant
- **AND** Groq provider SHALL be selected
- **AND** answer SHALL be generated using Groq
- **AND** response metadata SHALL include provider="groq"
- **AND** response metadata SHALL include timing for each stage

#### Scenario: Generate answer with OpenAI (fallback)

- **GIVEN** Groq provider returns error
- **AND** OpenAI is configured as fallback
- **WHEN** retrieve_documents() is called with retry
- **THEN** system SHALL automatically try OpenAI
- **AND** answer SHALL be generated successfully
- **AND** metadata SHALL indicate fallback occurred

#### Scenario: Generate answer with Anthropic (quality strategy)

- **GIVEN** query complexity is "complex"
- **AND** LLM_PROVIDER_STRATEGY is "quality"
- **WHEN** retrieve_documents() is called
- **THEN** Anthropic Claude SHALL be used
- **AND** higher quality answer SHALL be generated
- **AND** provider cost SHALL be logged

### Requirement: Streaming Answer Generation

The system SHALL stream LLM-generated tokens incrementally to clients via Server-Sent Events, supporting all configured providers through aisuite's unified streaming interface.

**Modified behavior**: Streaming now works across all aisuite providers (OpenAI, Anthropic, Groq) with normalized token format and consistent SSE delivery.

#### Scenario: Stream tokens from Groq

- **GIVEN** streaming is enabled
- **AND** Groq provider is selected
- **WHEN** retrieve_documents_streaming() is called
- **THEN** documents event SHALL be yielded first
- **AND** tokens SHALL stream from Groq
- **AND** done event SHALL include provider="groq"
- **AND** timing metadata SHALL be included

#### Scenario: Stream tokens from Anthropic

- **GIVEN** streaming is enabled
- **AND** Anthropic provider is selected
- **WHEN** retrieve_documents_streaming() is called
- **THEN** tokens SHALL stream using Anthropic format
- **AND** aisuite SHALL normalize the stream
- **AND** SSE format SHALL match Phase 2 specification

#### Scenario: Stream with provider override

- **GIVEN** streaming is enabled
- **AND** provider="anthropic" is specified in request
- **WHEN** retrieve_documents_streaming() is called
- **THEN** Anthropic SHALL be used regardless of complexity
- **AND** streaming SHALL work correctly
- **AND** override SHALL be logged

### Requirement: Error Handling and Retry

The system SHALL implement robust error handling with automatic retry logic and multi-provider fallback to ensure high availability and resilience against transient failures.

**Modified behavior**: Retry logic now handles provider-specific errors and implements intelligent fallback through provider chain (primary → fallback → premium).

#### Scenario: Retry with same provider

- **GIVEN** Groq returns transient 429 Rate Limit
- **WHEN** generate attempt fails
- **THEN** system SHALL retry with exponential backoff
- **AND** same provider SHALL be used (up to 3 times)
- **AND** if all retries fail, fallback SHALL trigger

#### Scenario: Fallback to next provider

- **GIVEN** all retries exhausted for primary provider
- **WHEN** fallback is triggered
- **THEN** next provider in chain SHALL be attempted
- **AND** full retry logic SHALL apply to fallback provider
- **AND** if fallback succeeds, response SHALL indicate provider used

#### Scenario: All providers exhausted

- **GIVEN** primary and fallback providers both fail
- **WHEN** premium provider is unavailable
- **THEN** ExternalServiceError SHALL be raised
- **AND** error message SHALL list all attempted providers
- **AND** user SHALL see 503 Service Unavailable

## ADDED Requirements

### Requirement: Query Complexity Detection

The pipeline SHALL detect query complexity before LLM invocation to enable smart routing.

#### Scenario: Detect simple query

- **GIVEN** query is "What is the capital of France?"
- **WHEN** complexity detection runs
- **THEN** complexity SHALL be classified as "simple"
- **AND** Groq SHALL be selected (if strategy=speed)

#### Scenario: Detect complex query

- **GIVEN** query is "Analyze the geopolitical implications of cryptocurrency adoption across developing nations with emphasis on monetary policy sovereignty"
- **WHEN** complexity detection runs
- **THEN** complexity SHALL be classified as "complex"
- **AND** Anthropic SHALL be selected (if strategy=quality)

### Requirement: Provider Performance Logging

The pipeline SHALL log provider selection and performance for monitoring and optimization.

#### Scenario: Log successful provider use

- **GIVEN** query is processed successfully
- **WHEN** response is returned
- **THEN** log SHALL include selected provider
- **AND** log SHALL include generation time
- **AND** log SHALL include token count (if available)
- **AND** log SHALL include request ID for correlation

#### Scenario: Log provider fallback

- **GIVEN** primary provider fails
- **WHEN** fallback occurs
- **THEN** log SHALL include both providers
- **AND** log SHALL include failure reason
- **AND** log SHALL include total retry time
- **AND** alert metric SHALL increment

## REMOVED Requirements

None. Existing pipeline functionality preserved, enhanced with multi-provider support.
