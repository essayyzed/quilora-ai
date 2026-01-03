# When to Create OpenSpec Proposals

A quick-reference guide for deciding when to use OpenSpec's formal proposal process vs. direct implementation.

## Decision Flowchart

```
New Request/Change
    │
    ▼
Is it urgent/critical (security vulnerability, production down)?
    ├─ YES → Fix immediately, create retroactive proposal if architectural
    └─ NO → Continue
         │
         ▼
Is it a bug fix restoring intended behavior?
    ├─ YES → Fix directly (document in commit message)
    └─ NO → Continue
         │
         ▼
Is it adding NEW functionality/capabilities?
    ├─ YES → CREATE PROPOSAL
    └─ NO → Continue
         │
         ▼
Is it a BREAKING change (API, schema, behavior)?
    ├─ YES → CREATE PROPOSAL
    └─ NO → Continue
         │
         ▼
Is it an architecture/infrastructure change?
    ├─ YES → CREATE PROPOSAL
    └─ NO → Continue
         │
         ▼
Will it take >2 hours or touch >5 files?
    ├─ YES → Consider lightweight proposal
    └─ NO → Continue
         │
         ▼
Is it code quality/maintenance work?
    ├─ YES → Implement directly, group in monthly maintenance proposal
    └─ NO → When in doubt, CREATE PROPOSAL (safer)
```

## Quick Reference Table

| Change Type                           | OpenSpec? | Example                       |
| ------------------------------------- | --------- | ----------------------------- |
| New API endpoint                      | ✅ YES    | Adding POST /documents        |
| New feature                           | ✅ YES    | Adding document OCR           |
| Breaking API change                   | ✅ YES    | Changing response schema      |
| Architecture change                   | ✅ YES    | Adding new service            |
| Security pattern change               | ✅ YES    | Changing auth flow            |
| Performance optimization (behavioral) | ✅ YES    | Caching strategy              |
| Infrastructure change                 | ✅ YES    | Adding Redis                  |
| Bug fix (restore spec behavior)       | ❌ NO     | Fixing incorrect return value |
| Code quality                          | ❌ NO     | Renaming variables            |
| Formatting/linting                    | ❌ NO     | Running Black                 |
| Adding type hints                     | ❌ NO     | Type annotations              |
| Removing dead code                    | ❌ NO     | Deleting unused function      |
| Dependency update (patch/minor)       | ❌ NO     | Updating pytest               |
| Documentation updates                 | ❌ NO     | Fixing typos                  |
| Test improvements                     | ❌ NO     | Adding test cases             |

## Detailed Guidelines

### ✅ ALWAYS Create Proposal For:

1. **New Capabilities**

   - New API endpoints
   - New user-facing features
   - New integrations (external services)
   - New pipeline components

2. **Breaking Changes**

   - API contract changes (request/response format)
   - Database schema changes
   - Configuration format changes
   - Removing existing features

3. **Architectural Decisions**

   - New design patterns (e.g., singleton, repository)
   - Adding new services or databases
   - Changing communication patterns
   - Significant refactoring (>5 files)

4. **Security Changes**
   - Authentication/authorization changes
   - Data encryption changes
   - Access control modifications
   - Security pattern implementations

### ⚠️ CONSIDER Proposal For:

1. **Large Refactoring**

   - Touches >5 files
   - Takes >2 hours
   - Changes internal APIs

2. **Performance Optimizations**

   - If behavior changes (even subtly)
   - If affects user experience
   - If involves caching strategy

3. **Dependency Changes**
   - Major version upgrades
   - Replacing core libraries
   - Adding new frameworks

### ❌ Skip Proposal For:

1. **Bug Fixes**

   - Restoring intended behavior
   - Fixing crashes
   - Correcting typos in logic

2. **Code Quality**

   - Variable renaming
   - Dead code removal
   - Type hint additions
   - Exception handling improvements
   - Code formatting

3. **Maintenance**

   - Dependency updates (patch/minor)
   - Documentation updates
   - Log message improvements
   - Comment additions

4. **Tests**
   - Adding tests for existing code
   - Fixing broken tests
   - Test refactoring

## Proposal Types

### Full Proposal (Big Changes)

```
openspec/changes/<change-id>/
├── proposal.md      # Complete RFC with rationale
├── tasks.md         # Detailed implementation checklist
├── design.md        # Architecture diagrams (optional)
└── specs/           # Delta specs per capability
    └── <capability>/
        └── spec.md
```

**Use for:** New features, breaking changes, architecture decisions

### Lightweight Proposal (Medium Changes)

```
openspec/changes/<change-id>/
├── proposal.md      # Brief: what/why/impact
└── tasks.md         # Simple checklist
```

**Use for:** Significant refactoring, cross-cutting improvements

### Retroactive Proposal (Already Implemented)

```
openspec/changes/<change-id>/
├── proposal.md      # Document what was done and why
└── tasks.md         # All items marked [x]
```

**Use for:** Architectural decisions made during urgent fixes, grouped maintenance work

## Monthly Maintenance Pattern

For code quality work, consider grouping into monthly maintenance proposals:

```
openspec/changes/maintenance-2026-01/
├── proposal.md      # Summary of all maintenance work
└── tasks.md         # Grouped by category
```

This provides an audit trail without proposal overhead for each small fix.

## Questions to Ask

Before implementing, ask yourself:

1. **"Would a future developer need to understand this decision?"**

   - YES → Create proposal (documents the "why")
   - NO → Implement directly

2. **"Could this break existing functionality?"**

   - YES → Create proposal (forces careful analysis)
   - NO → Likely safe to implement directly

3. **"Am I changing HOW the system works, or just cleaning it up?"**

   - Changing behavior → Create proposal
   - Cleaning up → Implement directly

4. **"Will this require coordination with others?"**
   - YES → Create proposal (alignment tool)
   - NO → Use judgment based on complexity

## Examples from This Project

### Should Have Used Proposal:

- Singleton pattern for document store (architecture change)
- Security error handling (security pattern)
- aisuite → OpenAI decision (architecture divergence)

### Correctly Skipped Proposal:

- Variable renaming (code quality)
- Removing duplicate function (dead code)
- Exception handling fix (best practice)
- Type annotation fixes (code quality)
- Test corrections (maintenance)

## Process Summary

```
Full Proposal Flow:
  Request → Proposal → Review → Approval → Implement → Tests → Archive

Lightweight Flow:
  Request → Brief Proposal → Quick Review → Implement → Tests → Archive

Direct Implementation Flow:
  Request → Implement → Tests → Commit (document in message)

Retroactive Flow:
  Urgent Fix → Implement → Tests → Retroactive Proposal → Archive
```

---

**Remember:** OpenSpec is a tool for thoughtful development, not bureaucracy. Use it when it adds value (documentation, alignment, careful analysis), skip it when it's just overhead.
