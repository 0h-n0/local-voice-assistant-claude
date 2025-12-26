# Implementation Plan: LLM Text Response Service

**Branch**: `003-llm-text-service` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-llm-text-service/spec.md`

## Summary

Implement an LLM text response service that accepts text messages and generates Japanese language responses using OpenAI's API. The service maintains conversation context via client-provided conversation IDs, uses a fixed system prompt for consistent Japanese assistant behavior, and provides health status endpoints. This integrates with the existing FastAPI backend alongside the STT service.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Pydantic v2, OpenAI Python SDK, httpx (async HTTP)
**Storage**: In-memory conversation cache (dict with TTL eviction)
**Testing**: pytest with pytest-asyncio
**Target Platform**: Linux server (same as existing backend)
**Project Type**: Web application (backend service)
**Performance Goals**: 95% of requests complete in <5 seconds (LLM latency dependent)
**Constraints**: Max 10 concurrent requests, max 4000 chars per message, max 20 messages per conversation
**Scale/Scope**: Single-user local assistant, in-memory state (no persistence)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ⚠️ VIOLATION | **Requires justification**: OpenAI API sends text to external server |
| II. Performance-Conscious | ✅ PASS | <5s target for LLM responses, streaming support planned |
| III. Simplicity-First | ✅ PASS | Minimal dependencies, in-memory storage, no over-engineering |
| IV. Test-Driven Development | ✅ PASS | TDD workflow, mock OpenAI client for testing |
| V. Modular Architecture | ✅ PASS | LLM service as separate module from STT, clear interfaces |
| VI. Observability | ✅ PASS | Structured logging, timing metrics for LLM calls |
| VII. Language-Idiomatic | ✅ PASS | uv, pydantic, ruff, mypy strict, async/await |

### Privacy Violation Justification

The Constitution's Privacy-First principle states:
> "All voice processing and AI inference MUST occur locally... Network requests are PROHIBITED except for optional, user-initiated features"

**Justification**: This feature explicitly requests OpenAI integration per user specification. The user has chosen to use an external LLM service, making this an "optional, user-initiated feature." The implementation will:
1. Require explicit API key configuration (opt-in)
2. Document clearly that text is sent to OpenAI
3. Keep feature disabled if no API key is configured
4. Never send audio data (only processed text from STT)

This is a conscious trade-off: high-quality LLM responses vs. local-only processing. The user made this decision in the feature request.

## Project Structure

### Documentation (this feature)

```text
specs/003-llm-text-service/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI spec)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── health.py       # Existing
│   │   ├── stt.py          # Existing
│   │   └── llm.py          # NEW: LLM API endpoints
│   ├── models/
│   │   ├── health.py       # Existing
│   │   ├── stt.py          # Existing
│   │   └── llm.py          # NEW: LLM request/response models
│   ├── services/
│   │   ├── stt_service.py  # Existing
│   │   └── llm_service.py  # NEW: LLM service logic
│   ├── dependencies.py     # Add LLM service dependency
│   └── main.py             # Register LLM router
├── tests/
│   ├── unit/
│   │   └── test_llm_service.py    # NEW
│   ├── integration/
│   │   └── test_llm_api.py        # NEW
│   └── contract/                   # NEW (optional)
└── pyproject.toml          # Add openai dependency
```

**Structure Decision**: Follows existing backend structure. LLM service added as new module alongside STT service with same patterns (service class, API router, Pydantic models).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| External API (OpenAI) | User explicitly requested OpenAI/gpt-5-mini integration | Local LLM would require significant GPU resources and model management; user specified external service |
