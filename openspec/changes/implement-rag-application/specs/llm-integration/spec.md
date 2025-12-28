# Delta for LLM Integration Specification

## ADDED Requirements

### Requirement: Multi-Provider LLM Support
The system SHALL support multiple LLM providers through aisuite.

#### Scenario: Use Groq provider (Primary)
- GIVEN the configuration specifies "groq:llama-3.3-70b-versatile"
- WHEN generating an answer
- THEN the system SHALL use aisuite to call Groq's API
- AND leverage free tier with high speed (300+ tokens/sec)
- AND pass the prompt and parameters
- AND return the generated response

#### Scenario: Use OpenAI provider (Fallback)
- GIVEN the configuration specifies "openai:gpt-4o-mini"
- WHEN generating an answer
- THEN the system SHALL use aisuite to call OpenAI's API
- AND optimize for cost ($0.15/1M tokens)
- AND pass the prompt and parameters
- AND return the generated response

#### Scenario: Use Anthropic provider (Premium)
- GIVEN the configuration specifies "anthropic:claude-3-5-sonnet-20240620"
- WHEN a complex or critical query is made
- THEN the system SHALL use aisuite to call Anthropic's API
- AND leverage superior reasoning capabilities
- AND pass the prompt and parameters
- AND return the generated response

#### Scenario: Switch providers via configuration
- GIVEN the LLM_PROVIDER environment variable is changed
- WHEN the application restarts
- THEN the system SHALL use the new provider
- AND NOT require code changes

### Requirement: Haystack Component Integration
The system SHALL provide a Haystack-compatible LLM component using aisuite.

#### Scenario: Component in pipeline
- GIVEN the AISuiteLLM component is added to a Haystack pipeline
- WHEN the pipeline runs
- THEN the component SHALL receive the prompt as input
- AND call aisuite.Client.chat.completions.create()
- AND return replies in Haystack format: {"replies": [str]}

#### Scenario: Component with parameters
- GIVEN the component is initialized with temperature=0.7
- WHEN generating a response
- THEN the system SHALL pass temperature to the LLM provider
- AND respect other parameters (max_tokens, top_p)

### Requirement: Streaming Support
The system SHALL support streaming responses from LLMs.

#### Scenario: Stream enabled
- GIVEN a request with stream=True
- WHEN generating an answer
- THEN the system SHALL stream tokens as they arrive
- AND yield each token incrementally
- AND signal completion when done

#### Scenario: Stream disabled
- GIVEN a request with stream=False
- WHEN generating an answer
- THEN the system SHALL wait for the complete response
- AND return the full text at once

### Requirement: Error Handling and Fallback
The system SHALL handle LLM provider failures gracefully.

#### Scenario: Rate limit exceeded
- GIVEN the LLM provider returns a rate limit error (429)
- WHEN generating a response
- THEN the system SHALL implement exponential backoff
- AND retry up to 3 times
- AND fail with a descriptive error if all retries fail

#### Scenario: Invalid API key
- GIVEN the API key is invalid or expired
- WHEN attempting to call the LLM
- THEN the system SHALL catch the authentication error
- AND return HTTP 500 with message "LLM authentication failed"
- AND log the error for debugging

#### Scenario: Automatic provider fallback
- GIVEN the primary provider (Groq) fails or times out
- WHEN processing a query
- THEN the system SHALL automatically retry with fallback provider (GPT-4o-mini)
- AND log the provider switch with reason
- AND track fallback frequency for monitoring
- AND escalate to premium provider if fallback also fails (optional)

### Requirement: Token Tracking
The system SHALL track token usage for cost monitoring.

#### Scenario: Track input and output tokens
- GIVEN a request is made to the LLM
- WHEN the response is received
- THEN the system SHALL extract token counts from the response
- AND log: prompt_tokens, completion_tokens, total_tokens
- AND include provider name in logs

### Requirement: Context Window Management
The system SHALL respect token limits for different providers.

#### Scenario: Truncate long prompts
- GIVEN a prompt exceeds the provider's context window
- WHEN preparing the request
- THEN the system SHALL truncate the prompt to fit
- AND prioritize the most recent/relevant context
- AND log a warning about truncation

### Requirement: Response Validation
The system SHALL validate LLM responses before returning them.

#### Scenario: Empty response
- GIVEN the LLM returns an empty or null response
- WHEN processing the output
- THEN the system SHALL detect the empty response
- AND return a fallback message: "Unable to generate response"
- AND log the issue

#### Scenario: Malformed response
- GIVEN the LLM returns unexpected format
- WHEN parsing the response
- THEN the system SHALL handle the parsing error
- AND return a user-friendly error message
- AND log the raw response for debugging
