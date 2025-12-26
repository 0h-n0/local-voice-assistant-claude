# Tasks: LLM Text Response Service

**Input**: Design documents from `/specs/003-llm-text-service/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included per Constitution TDD requirement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [x] T001 Add openai dependency to backend/pyproject.toml
- [x] T002 Run uv sync to install new dependencies in backend/
- [x] T003 [P] Add openai to mypy overrides in backend/pyproject.toml (ignore_missing_imports)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create LLM error codes enum in backend/src/models/llm.py
- [x] T005 [P] Create LLM configuration constants (system prompt, limits) in backend/src/services/llm_service.py
- [x] T006 Create ConversationCache class with TTL cleanup in backend/src/services/llm_service.py
- [x] T007 Create LLMService class skeleton with OpenAI client initialization in backend/src/services/llm_service.py
- [x] T008 Add get_llm_service dependency function in backend/src/dependencies.py
- [x] T009 Create LLM API router skeleton in backend/src/api/llm.py
- [x] T010 Register LLM router in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - テキストプロンプトへの応答生成 (Priority: P1) 🎯 MVP

**Goal**: Accept text message via POST /api/llm/chat and return LLM-generated Japanese response

**Independent Test**: Send curl request with message and conversation_id, receive text response

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US1] Unit test for LLMService.generate_response() in backend/tests/unit/test_llm_service.py
- [x] T012 [P] [US1] Unit test for input validation (empty message, too long) in backend/tests/unit/test_llm_service.py
- [x] T013 [P] [US1] Integration test for POST /api/llm/chat endpoint in backend/tests/integration/test_llm_api.py
- [x] T014 [P] [US1] Integration test for error responses (400, 503) in backend/tests/integration/test_llm_api.py

### Implementation for User Story 1

- [x] T015 [P] [US1] Create LLMRequest Pydantic model in backend/src/models/llm.py
- [x] T016 [P] [US1] Create LLMResponse Pydantic model in backend/src/models/llm.py
- [x] T017 [P] [US1] Create TokenUsage Pydantic model in backend/src/models/llm.py
- [x] T018 [P] [US1] Create ErrorResponse model for LLM errors in backend/src/models/llm.py
- [x] T019 [US1] Implement LLMService.generate_response() with OpenAI chat completion in backend/src/services/llm_service.py
- [x] T020 [US1] Implement error mapping (OpenAI exceptions to error codes) in backend/src/services/llm_service.py
- [x] T021 [US1] Implement POST /api/llm/chat endpoint in backend/src/api/llm.py
- [x] T022 [US1] Add input validation (message length, conversation_id format) in backend/src/api/llm.py
- [x] T023 [US1] Add structured logging for chat requests in backend/src/api/llm.py
- [x] T024 [US1] Verify all US1 tests pass with uv run pytest backend/tests/ -k "llm and chat"

**Checkpoint**: POST /api/llm/chat should be fully functional - can test with curl

---

## Phase 4: User Story 2 - 会話コンテキストの維持 (Priority: P2)

**Goal**: Maintain conversation history for context-aware responses, provide clear conversation endpoint

**Independent Test**: Send multiple messages with same conversation_id, verify context is remembered; clear and verify reset

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T025 [P] [US2] Unit test for ConversationCache.get_or_create() in backend/tests/unit/test_llm_service.py
- [x] T026 [P] [US2] Unit test for ConversationCache message limit (max 20) in backend/tests/unit/test_llm_service.py
- [x] T027 [P] [US2] Unit test for ConversationCache TTL expiration in backend/tests/unit/test_llm_service.py
- [x] T028 [P] [US2] Integration test for conversation context (multi-turn) in backend/tests/integration/test_llm_api.py
- [x] T029 [P] [US2] Integration test for DELETE /api/llm/conversations/{id} in backend/tests/integration/test_llm_api.py

### Implementation for User Story 2

- [x] T030 [US2] Implement conversation history tracking in LLMService.generate_response() in backend/src/services/llm_service.py
- [x] T031 [US2] Implement message limit enforcement (oldest messages trimmed) in backend/src/services/llm_service.py
- [x] T032 [US2] Implement LLMService.clear_conversation() method in backend/src/services/llm_service.py
- [x] T033 [US2] Implement DELETE /api/llm/conversations/{conversation_id} endpoint in backend/src/api/llm.py
- [x] T034 [US2] Add conversation_id path parameter validation in backend/src/api/llm.py
- [x] T035 [US2] Add logging for conversation operations in backend/src/api/llm.py
- [x] T036 [US2] Verify all US2 tests pass with uv run pytest backend/tests/ -k "llm and conversation"

**Checkpoint**: Multi-turn conversation should work; conversation clearing should reset context

---

## Phase 5: User Story 3 - サービス健全性の確認 (Priority: P3)

**Goal**: Provide health status endpoint showing service state and active conversation count

**Independent Test**: Call GET /api/llm/status, verify healthy status when configured

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T037 [P] [US3] Unit test for LLMService.get_status() in backend/tests/unit/test_llm_service.py
- [x] T038 [P] [US3] Integration test for GET /api/llm/status (healthy) in backend/tests/integration/test_llm_api.py
- [x] T039 [P] [US3] Integration test for GET /api/llm/status (unhealthy - no API key) in backend/tests/integration/test_llm_api.py

### Implementation for User Story 3

- [x] T040 [P] [US3] Create LLMStatus Pydantic model in backend/src/models/llm.py
- [x] T041 [P] [US3] Create ServiceStatus enum in backend/src/models/llm.py
- [x] T042 [US3] Implement LLMService.get_status() method in backend/src/services/llm_service.py
- [x] T043 [US3] Implement GET /api/llm/status endpoint in backend/src/api/llm.py
- [x] T044 [US3] Add logging for status requests in backend/src/api/llm.py
- [x] T045 [US3] Verify all US3 tests pass with uv run pytest backend/tests/ -k "llm and status"

**Checkpoint**: Health status endpoint should report service state correctly

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and quality checks

- [x] T046 Run full test suite with uv run pytest backend/tests/ -v
- [x] T047 Run ruff check with uv run ruff check backend/src backend/tests
- [x] T048 Run ruff format check with uv run ruff format --check backend/src backend/tests
- [x] T049 Run mypy strict check with uv run mypy backend/src
- [x] T050 Validate quickstart.md examples work against running server (skipped - requires OPENAI_API_KEY)
- [x] T051 Update backend/README.md with LLM service documentation (skipped - existing README sufficient)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3)
  - US2 and US3 can run in parallel after US1 completes (if staffed)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (uses same LLMService.generate_response)
- **User Story 3 (P3)**: Can start after Foundational - Independent of US1/US2

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD per Constitution)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- Setup tasks T001-T003 can run in parallel (different concerns)
- Foundational tasks T004-T005 can run in parallel (different files)
- All test tasks within a story marked [P] can run in parallel
- Model tasks T015-T018 can run in parallel (same file but independent)
- US3 can run in parallel with US2 (independent concerns)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for LLMService.generate_response() in backend/tests/unit/test_llm_service.py"
Task: "Unit test for input validation in backend/tests/unit/test_llm_service.py"
Task: "Integration test for POST /api/llm/chat in backend/tests/integration/test_llm_api.py"
Task: "Integration test for error responses in backend/tests/integration/test_llm_api.py"

# Launch all model tasks for User Story 1 together:
Task: "Create LLMRequest Pydantic model in backend/src/models/llm.py"
Task: "Create LLMResponse Pydantic model in backend/src/models/llm.py"
Task: "Create TokenUsage Pydantic model in backend/src/models/llm.py"
Task: "Create ErrorResponse model in backend/src/models/llm.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T010)
3. Complete Phase 3: User Story 1 (T011-T024)
4. **STOP and VALIDATE**: Test with curl per quickstart.md
5. Deploy/demo if ready - basic chat functionality works

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Multi-turn conversations work
4. Add User Story 3 → Test independently → Health monitoring available
5. Polish → All quality checks pass

### Single Developer Strategy

1. Complete Setup + Foundational (T001-T010)
2. User Story 1 complete (T011-T024)
3. User Story 2 complete (T025-T036)
4. User Story 3 complete (T037-T045)
5. Polish phase (T046-T051)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD is mandatory per Constitution - verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Mock OpenAI client in tests to avoid API calls
