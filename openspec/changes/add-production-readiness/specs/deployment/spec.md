# Delta for Deployment Specification - Production Readiness (Phase 2)

## ADDED Requirements

### Requirement: Docker Containerization

The system SHALL provide Docker containers for reproducible deployment.

#### Scenario: Build backend Docker image

- GIVEN the project source code
- WHEN the Dockerfile is built
- THEN the system SHALL create a multi-stage image
- AND use Python 3.11 slim as base
- AND install production dependencies only (no dev deps)
- AND copy source code with correct permissions
- AND expose port 8000
- AND set non-root user for security

#### Scenario: Run backend container

- GIVEN a built Docker image
- WHEN the container is started with proper environment variables
- THEN the system SHALL start the FastAPI application
- AND listen on the specified host and port
- AND connect to Qdrant using container networking
- AND serve requests successfully

---

### Requirement: Docker Compose Orchestration

The system SHALL provide docker-compose.yml for easy local deployment.

#### Scenario: Start all services

- GIVEN a docker-compose.yml file
- WHEN `docker compose up` is executed
- THEN the system SHALL start Qdrant container
- AND start FastAPI backend container
- AND create a shared network for inter-service communication
- AND expose Qdrant on port 6333
- AND expose API on port 8000
- AND wait for Qdrant to be healthy before starting backend

#### Scenario: Persist Qdrant data

- GIVEN Docker Compose is running
- WHEN documents are indexed
- THEN the system SHALL store vectors in a named volume
- AND persist the volume across container restarts
- AND NOT lose data when containers are stopped

#### Scenario: Environment configuration

- GIVEN a .env file with configuration
- WHEN Docker Compose starts
- THEN the system SHALL load environment variables from .env
- AND pass them to the backend container
- AND NOT expose secrets in docker-compose.yml
- AND validate required variables are set

---

### Requirement: CI/CD Pipeline

The system SHALL automatically test code on every push and pull request.

#### Scenario: Run tests on push

- GIVEN code is pushed to the main branch
- WHEN the GitHub Actions workflow triggers
- THEN the system SHALL check out the code
- AND set up Python 3.11
- AND install dependencies with uv
- AND run pytest with all tests
- AND fail the workflow if tests fail

#### Scenario: Run linting checks

- GIVEN code is pushed or PR is opened
- WHEN the linting workflow triggers
- THEN the system SHALL check code formatting with black
- AND check import sorting with isort
- AND check code quality with ruff
- AND fail the workflow if any check fails

#### Scenario: Check test coverage

- GIVEN tests are executed in CI
- WHEN pytest completes
- THEN the system SHALL generate a coverage report
- AND fail if coverage is below 70%
- AND upload coverage to GitHub Actions artifacts

---

### Requirement: Production Configuration

The system SHALL provide secure configuration for production deployment.

#### Scenario: Environment-based configuration

- GIVEN the application is deployed
- WHEN it starts
- THEN the system SHALL load configuration from environment variables
- AND validate all required variables are present
- AND use secure defaults where appropriate
- AND log configuration status (without exposing secrets)

#### Scenario: Secret management

- GIVEN sensitive credentials are needed
- WHEN the application loads configuration
- THEN the system SHALL read API keys from environment only
- AND NOT log API keys
- AND NOT expose API keys in error messages
- AND mask API keys in health check responses

#### Scenario: CORS configuration

- GIVEN the API is deployed
- WHEN requests come from web clients
- THEN the system SHALL enforce CORS policy
- AND allow configured origins only (not wildcard in production)
- AND reject requests from unauthorized origins

---

### Requirement: Logging Configuration

The system SHALL provide structured JSON logging for production.

#### Scenario: JSON log format

- GIVEN the application is running in production
- WHEN log events are emitted
- THEN the system SHALL format logs as JSON
- AND include timestamp in ISO format
- AND include log level (INFO, WARNING, ERROR, etc.)
- AND include logger name
- AND include message and any metadata

#### Scenario: Log rotation

- GIVEN the application is running
- WHEN logs are written to disk
- THEN the system SHALL rotate logs daily
- AND compress old logs
- AND retain logs for 7 days
- AND delete logs older than 7 days

#### Scenario: Log level configuration

- GIVEN the application starts
- WHEN LOG_LEVEL environment variable is set
- THEN the system SHALL use that log level
- AND default to INFO if not specified
- AND support DEBUG, INFO, WARNING, ERROR, CRITICAL
