<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0 (Technical stack and workflow expansion)
Modified principles:
  - VII. Python-Idiomatic → Updated to include uv, pydantic, ruff requirements
Added sections:
  - Technical Stack (new section with frontend/backend specifications)
  - Branch & PR Workflow (expanded Development Workflow)
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Technical Context section exists)
  - .specify/templates/spec-template.md: ✅ Compatible
  - .specify/templates/tasks-template.md: ✅ Compatible (web app structure documented)
Follow-up TODOs: None
-->

# Local Voice Assistant Constitution

## Core Principles

### I. Privacy-First (NON-NEGOTIABLE)

All voice processing and AI inference MUST occur locally on the user's device. No audio
data, transcriptions, or conversation content shall be transmitted to external servers
unless explicitly enabled by the user for a specific, documented purpose.

**Requirements**:
- Audio capture and processing MUST use local-only libraries
- LLM inference MUST run on-device (e.g., llama.cpp, whisper.cpp)
- Network requests are PROHIBITED except for optional, user-initiated features
- Any network feature MUST be disabled by default with clear opt-in

**Rationale**: Users trust voice assistants with intimate conversations. Betraying that
trust by sending data externally violates the core value proposition of a *local* assistant.

### II. Performance-Conscious

The assistant MUST respond with low latency and efficient resource usage to provide a
natural conversational experience without degrading system performance.

**Requirements**:
- Voice activity detection to response MUST complete in <500ms on target hardware
- Memory footprint MUST stay under defined limits (document in plan.md)
- CPU/GPU usage MUST be profiled and optimized for sustained use
- Streaming responses preferred over batch processing where applicable

**Rationale**: A slow voice assistant breaks conversational flow. Users will abandon
tools that make them wait or slow down their machines.

### III. Simplicity-First

Start with the simplest solution that works. Avoid premature abstraction, over-engineering,
and speculative features. Every component MUST justify its complexity.

**Requirements**:
- YAGNI (You Aren't Gonna Need It) strictly enforced
- No abstractions until the third concrete use case
- Configuration MUST have sensible defaults; zero-config startup preferred
- Dependencies MUST be minimal and justified

**Rationale**: Complexity is the enemy of maintainability. Simple systems are easier to
debug, extend, and reason about.

### IV. Test-Driven Development (NON-NEGOTIABLE)

All features MUST follow the TDD cycle: write failing tests first, implement to pass,
then refactor. No production code without corresponding tests.

**Requirements**:
- Red-Green-Refactor cycle strictly enforced
- Tests MUST be written and failing BEFORE implementation begins
- Test coverage MUST include: unit tests, integration tests, contract tests where applicable
- Mocking external dependencies (microphone, speakers) for testability

**Rationale**: TDD ensures correctness, documents behavior, enables confident refactoring,
and prevents regression. Voice systems are notoriously hard to test—TDD makes it tractable.

### V. Modular Architecture

The system MUST be composed of loosely-coupled, independently testable modules with
clear interfaces between components.

**Requirements**:
- Clear separation: audio capture, speech-to-text, LLM, text-to-speech, orchestration
- Each module MUST be independently runnable and testable via CLI
- Inter-module communication via well-defined interfaces (not shared state)
- Modules MUST NOT have circular dependencies

**Rationale**: Modularity enables independent development, testing, and replacement of
components (e.g., swapping STT engines without touching LLM logic).

### VI. Observability

All operations MUST be traceable through structured logging and metrics for debugging
and performance optimization.

**Requirements**:
- Structured logging (JSON format) for all significant operations
- Timing metrics for each pipeline stage (capture, STT, LLM, TTS)
- Debug mode MUST expose full pipeline visibility
- Logs MUST be local-only (respecting Privacy-First principle)

**Rationale**: Voice pipelines have many failure modes. Without observability, debugging
is guesswork.

### VII. Language-Idiomatic Code

Code MUST follow language-specific best practices, leveraging each language's strengths
while avoiding common pitfalls.

**Python (Backend) Requirements**:
- Package management via `uv` (NOT pip, poetry, or pipenv)
- Type validation via `pydantic` for all data models and API contracts
- Linting and formatting via `ruff` (replaces flake8, black, isort)
- Type hints MUST be used throughout (mypy strict mode compatible)
- Use async/await for I/O-bound operations

**TypeScript (Frontend) Requirements**:
- Strict TypeScript mode enabled
- ESLint + Prettier for linting and formatting
- Prefer functional components with hooks
- Type definitions for all props and state

**Rationale**: Consistent, idiomatic code is easier to read, review, and maintain.
Strong typing catches errors early and serves as documentation.

## Technical Stack

### Frontend

| Aspect | Technology | Notes |
|--------|------------|-------|
| Framework | Next.js (React) | App Router preferred |
| Language | TypeScript | Strict mode |
| Styling | TBD | Define in plan.md |
| State | TBD | Define in plan.md |
| Testing | Jest + React Testing Library | |

### Backend

| Aspect | Technology | Notes |
|--------|------------|-------|
| Framework | FastAPI | Async-first |
| Language | Python 3.11+ | |
| Package Manager | uv | NOT pip/poetry |
| Type Validation | Pydantic v2 | All models |
| Linting | ruff | Zero warnings |
| Type Checking | mypy (strict) | |
| Testing | pytest | With pytest-asyncio |

### Project Structure

```text
frontend/
├── src/
│   ├── app/           # Next.js App Router
│   ├── components/    # React components
│   ├── hooks/         # Custom hooks
│   ├── lib/           # Utilities
│   └── types/         # TypeScript types
├── tests/
└── package.json

backend/
├── src/
│   ├── api/           # FastAPI routes
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   └── lib/           # Utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
└── pyproject.toml     # uv managed
```

## Development Workflow

### Branch & PR Workflow (NON-NEGOTIABLE)

Every feature MUST follow this workflow:

1. **Create feature branch** before any code changes
   - Branch naming: `feature/###-description` or `fix/###-description`
   - Branch from `main` (or designated development branch)

2. **Implement feature** following TDD and Constitution principles

3. **Update README.md** after implementation
   - Document new features, configuration changes, or usage instructions
   - Keep README current with project state

4. **Create Pull Request** for review
   - PR MUST include: summary, test plan, Constitution compliance checklist
   - Self-review before requesting others

5. **Code Review** required before merge
   - Reviewer MUST verify Constitution compliance
   - All CI checks MUST pass
   - Address all review comments

### Code Review Requirements

- All changes MUST be reviewed before merge
- Reviewers MUST verify Constitution compliance (use checklist)
- Performance-sensitive changes require benchmark comparison
- README updates verified for accuracy

### Testing Gates

- All tests MUST pass before merge
- New features MUST include tests (TDD)
- Coverage MUST NOT decrease without justification
- Both frontend and backend tests required for full-stack features

### Quality Standards

**Backend (Python)**:
- `uv run ruff check .` MUST pass with zero warnings
- `uv run ruff format --check .` MUST pass
- `uv run mypy --strict .` MUST pass
- Pydantic models for all API request/response types

**Frontend (TypeScript)**:
- `npm run lint` (ESLint) MUST pass
- `npm run typecheck` (tsc --noEmit) MUST pass
- `npm run format:check` (Prettier) MUST pass

## Governance

This Constitution is the supreme authority for project decisions. All development
practices, code reviews, and architectural choices MUST comply with these principles.

### Amendment Process

1. Propose amendment with rationale in a dedicated PR
2. Document impact on existing code and templates
3. Obtain maintainer approval
4. Update version number according to semantic versioning:
   - MAJOR: Principle removal or incompatible redefinition
   - MINOR: New principle or significant expansion
   - PATCH: Clarifications, wording improvements
5. Update dependent templates as needed

### Compliance

- Every PR/review MUST verify Constitution compliance
- Violations require explicit justification in Complexity Tracking
- Runtime guidance lives in project documentation (README, docs/)

**Version**: 1.1.0 | **Ratified**: 2025-12-25 | **Last Amended**: 2025-12-25
