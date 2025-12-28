# Delta for Frontend Specification

## ADDED Requirements

### Requirement: Chat Interface
The system SHALL provide a conversational interface for users to query documents.

#### Scenario: Display chat history
- GIVEN previous queries and responses exist
- WHEN the user views the chat interface
- THEN the system SHALL display messages in chronological order
- AND distinguish between user questions and AI responses
- AND show timestamps for each message

#### Scenario: Submit query
- GIVEN a user types a question in the input field
- WHEN the user presses Enter or clicks Send
- THEN the system SHALL send the query to the backend
- AND display the query immediately in the chat
- AND show a loading indicator while waiting for response

#### Scenario: Receive streaming response
- GIVEN a query is submitted with streaming enabled
- WHEN the backend streams the response
- THEN the frontend SHALL display tokens as they arrive
- AND update the message incrementally
- AND show a typing indicator during streaming

### Requirement: Document Upload
The system SHALL allow users to upload documents for indexing.

#### Scenario: Upload file via button
- GIVEN a user clicks the upload button
- WHEN a file is selected
- THEN the system SHALL validate the file type (PDF, TXT, MD, DOCX)
- AND validate file size (max 10MB)
- AND show a progress indicator during upload
- AND display success message on completion

#### Scenario: Drag and drop upload
- GIVEN a user drags a file over the upload area
- WHEN the file is dropped
- THEN the system SHALL accept the file
- AND process it as with button upload
- AND show visual feedback during drag

#### Scenario: Upload failure
- GIVEN a file upload fails (network error, invalid file, etc.)
- WHEN the error occurs
- THEN the system SHALL display an error message
- AND allow the user to retry
- AND NOT add the document to the list

### Requirement: Document Management
The system SHALL display and manage uploaded documents.

#### Scenario: List documents
- GIVEN documents are uploaded and indexed
- WHEN the user views the documents list
- THEN the system SHALL fetch and display all documents
- AND show filename, upload date, and chunk count
- AND update the list when new documents are added

#### Scenario: Delete document
- GIVEN a document exists in the list
- WHEN the user clicks the delete button
- THEN the system SHALL prompt for confirmation
- AND remove the document from backend if confirmed
- AND update the UI to remove the document from the list

### Requirement: Error Handling
The system SHALL provide clear feedback for errors.

#### Scenario: Network error
- GIVEN the backend is unreachable
- WHEN the user attempts any action
- THEN the system SHALL display "Unable to connect to server"
- AND provide a retry button
- AND NOT crash or hang

#### Scenario: Query timeout
- GIVEN a query takes too long to respond
- WHEN the timeout threshold is reached (30 seconds)
- THEN the system SHALL stop waiting for response
- AND display "Request timed out, please try again"
- AND allow submitting a new query

#### Scenario: Invalid query
- GIVEN the backend returns a 400 error
- WHEN processing the response
- THEN the system SHALL display the error message from backend
- AND allow the user to submit a new query

### Requirement: Loading States
The system SHALL indicate when operations are in progress.

#### Scenario: Loading indicator for queries
- GIVEN a query is submitted
- WHEN waiting for the response
- THEN the system SHALL show a typing indicator or spinner
- AND disable the input field
- AND allow canceling the request

#### Scenario: Upload progress
- GIVEN a file is being uploaded
- WHEN the upload is in progress
- THEN the system SHALL show a progress bar
- AND display percentage or file size uploaded
- AND allow canceling the upload

### Requirement: Responsive Design
The system SHALL work on various screen sizes.

#### Scenario: Desktop view
- GIVEN the user accesses the app on a desktop
- WHEN viewing the interface
- THEN the system SHALL display chat and document list side by side
- AND optimize for keyboard navigation

#### Scenario: Mobile view
- GIVEN the user accesses the app on a mobile device
- WHEN viewing the interface
- THEN the system SHALL stack components vertically
- AND provide touch-friendly controls
- AND show mobile-optimized upload interface

### Requirement: Source Attribution
The system SHALL display sources for AI responses.

#### Scenario: Show document sources
- GIVEN an AI response is generated with retrieved context
- WHEN displaying the response
- THEN the system SHALL show which documents were used
- AND display chunk references if available
- AND allow clicking to view source content (optional)
