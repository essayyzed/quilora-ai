# Tasks: Code Quality Improvements - January 2026

## Status: COMPLETED ✅

## 1. Security Improvements

- [x] 1.1 Update API error handling to log internally and return generic message
- [x] 1.2 Add reserved keys protection to document metadata

## 2. Performance Improvements

- [x] 2.1 Implement thread-safe singleton for document store
- [x] 2.2 Add module-level caching for embedder

## 3. API Contract Fixes

- [x] 3.1 Update delete return value to -1 for unknown count
- [x] 3.2 Add validation with helpful error messages for settings

## 4. Code Quality Fixes

- [x] 4.1 Remove incorrect hasattr() check for Pydantic field
- [x] 4.2 Remove duplicate index_documents() function
- [x] 4.3 Rename shadowed variable in test fixture
- [x] 4.4 Replace bare except with proper exception handling
- [x] 4.5 Add policy parameter for Haystack compatibility

## 5. Test Improvements

- [x] 5.1 Update test assertions for new delete behavior
- [x] 5.2 Fix pipeline tests to use proper Document objects

## 6. Documentation

- [x] 6.1 Create CODE_REVIEW_IMPROVEMENTS.md with detailed changelog
- [x] 6.2 Create retroactive OpenSpec proposal

## Verification

- [x] All tests passing (11/11)
- [x] No regressions introduced
