# Tasks: Voice Dialogue Orchestrator

**Input**: Design documents from `/specs/005-voice-orchestrator/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Included based on project's TDD approach (Constitution IV).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization for orchestrator module

- [x] T001 Create orchestrator module directory structure (backend/src/api/, models/, services/)
- [x] T002 [P] Add orchestrator environment variables to backend/src/config.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and error handling that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create OrchestratorErrorCode enum in backend/src/models/orchestrator.py
- [x] T004 Create OrchestratorErrorResponse model in backend/src/models/orchestrator.py
- [x] T005 [P] Create HealthStatus enum in backend/src/models/orchestrator.py
- [x] T006 Create ProcessingMetadata model in backend/src/models/orchestrator.py
- [x] T007 Register orchestrator router in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 音声による質問と音声応答 (Priority: P1) 🎯 MVP

**Goal**: POST /api/orchestrator/dialogue - 音声入力を受け取り、STT→LLM→TTS パイプラインを実行し、音声応答を返却する

**Independent Test**: 音声ファイル（例: 「今日の天気は？」）をAPIに送信し、WAV形式の音声応答を受け取れることを確認

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Contract test for POST /api/orchestrator/dialogue in backend/tests/contract/test_orchestrator_contract.py
- [x] T009 [P] [US1] Unit tests for OrchestratorService pipeline in backend/tests/unit/test_orchestrator_service.py
- [x] T010 [P] [US1] Integration test for voice dialogue API in backend/tests/integration/test_orchestrator_api.py

### Implementation for User Story 1

- [x] T011 [US1] Create OrchestratorService class skeleton in backend/src/services/orchestrator_service.py
- [x] T012 [US1] Implement audio validation (format, duration) in OrchestratorService
- [x] T013 [US1] Implement STT step with error handling in OrchestratorService
- [x] T014 [US1] Implement LLM step with error handling in OrchestratorService
- [x] T015 [US1] Implement TTS step with error handling in OrchestratorService
- [x] T016 [US1] Implement full pipeline with timing metrics in OrchestratorService.process_dialogue()
- [x] T017 [US1] Add DI functions for OrchestratorService in backend/src/dependencies.py
- [x] T018 [US1] Create POST /api/orchestrator/dialogue endpoint in backend/src/api/orchestrator.py
- [x] T019 [US1] Add response headers (X-Processing-Time-*, X-Input-*, X-Output-*) to endpoint
- [x] T020 [US1] Implement semaphore-based concurrency control (max 5 concurrent requests)

**Checkpoint**: POST /api/orchestrator/dialogue should be fully functional

---

## Phase 4: User Story 2 - 処理ステータスの確認 (Priority: P2)

**Goal**: GET /api/orchestrator/status - 全サービス（STT/LLM/TTS）のヘルスステータスを集約して返却する

**Independent Test**: ステータスAPIを呼び出し、各サービス状態がJSON形式で返されることを確認

### Tests for User Story 2 ⚠️

- [x] T021 [P] [US2] Contract test for GET /api/orchestrator/status in backend/tests/contract/test_orchestrator_contract.py
- [x] T022 [P] [US2] Unit tests for status aggregation logic in backend/tests/unit/test_orchestrator_service.py
- [x] T023 [P] [US2] Integration test for status API in backend/tests/integration/test_orchestrator_api.py

### Implementation for User Story 2

- [x] T024 [US2] Create ServiceStatus model in backend/src/models/orchestrator.py
- [x] T025 [US2] Create OrchestratorStatus model in backend/src/models/orchestrator.py
- [x] T026 [US2] Implement get_status() method in OrchestratorService
- [x] T027 [US2] Implement status aggregation logic (healthy/degraded/unhealthy)
- [x] T028 [US2] Create GET /api/orchestrator/status endpoint in backend/src/api/orchestrator.py

**Checkpoint**: GET /api/orchestrator/status should be fully functional

---

## Phase 5: User Story 3 - エラー時の適切な応答 (Priority: P3)

**Goal**: 各処理ステップでのエラーを適切なHTTPステータスとエラーコードで返却する

**Independent Test**: 無効な音声ファイルや空リクエストを送信し、適切なエラーレスポンスを確認

### Tests for User Story 3 ⚠️

- [x] T029 [P] [US3] Test INVALID_AUDIO_FORMAT error (400) in backend/tests/unit/test_orchestrator_service.py
- [x] T030 [P] [US3] Test AUDIO_TOO_SHORT error (400) in backend/tests/unit/test_orchestrator_service.py
- [x] T031 [P] [US3] Test AUDIO_TOO_LONG error (400) in backend/tests/unit/test_orchestrator_service.py
- [x] T032 [P] [US3] Test SPEECH_RECOGNITION_FAILED error (422) in backend/tests/unit/test_orchestrator_service.py
- [x] T033 [P] [US3] Test service unavailable errors (503) in backend/tests/unit/test_orchestrator_service.py
- [x] T034 [P] [US3] Test TOO_MANY_REQUESTS error (429) in backend/tests/integration/test_orchestrator_api.py

### Implementation for User Story 3

- [x] T035 [US3] Create OrchestratorException class with error codes in backend/src/services/orchestrator_service.py
- [x] T036 [US3] Add exception handlers to orchestrator router in backend/src/api/orchestrator.py
- [x] T037 [US3] Implement retry_after logic for rate limit errors
- [x] T038 [US3] Add structured logging for all error cases

**Checkpoint**: All error scenarios should return appropriate HTTP status and error messages

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T039 Run ruff linter and fix issues
- [ ] T040 Run mypy --strict and fix type errors
- [ ] T041 [P] Run all tests (uv run pytest tests/ -v -k orchestrator)
- [ ] T042 [P] Validate quickstart.md examples manually
- [ ] T043 Update CLAUDE.md with orchestrator information

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (P1) → US2 (P2) → US3 (P3) in priority order
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Phase 2 - Independent of US1
- **User Story 3 (P3)**: Enhances US1 error handling - Best implemented after US1

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Foundational tasks marked [P] can run in parallel
- All tests for a user story marked [P] can run in parallel
- US1 and US2 can be implemented in parallel (different concerns)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test POST /api/orchestrator/dialogue independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test with curl → Deploy/Demo (MVP!)
3. Add User Story 2 → Test status endpoint → Deploy/Demo
4. Add User Story 3 → Test error scenarios → Deploy/Demo

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Existing services (STT, LLM, TTS) will be called via direct DI injection, not HTTP
