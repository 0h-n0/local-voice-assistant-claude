# Tasks: TTS API (Text-to-Speech)

**Input**: Design documents from `/specs/004-tts-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: This feature follows TDD per Constitution (Principle IV). Tests are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and TTS dependencies

- [x] T001 Add style-bert-vits2, torch, scipy dependencies to backend/pyproject.toml
- [x] T002 [P] Create TTS configuration settings in backend/src/config.py (TTS_MODEL_PATH, TTS_DEVICE, TTS_MAX_CONCURRENT)
- [x] T003 [P] Create model_assets directory structure for TTS models

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core TTS infrastructure that MUST be complete before ANY user story can be implemented

**Note**: No blocking foundational tasks required - all shared models/services are implemented within User Story 1 and reused by subsequent stories.

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - テキストから音声ファイル生成 (Priority: P1) 🎯 MVP

**Goal**: 日本語テキストを送信し、自然な音声ファイル (WAV) を受け取る

**Independent Test**: `curl -X POST "http://localhost:8000/api/tts/synthesize" -H "Content-Type: application/json" -d '{"text": "こんにちは"}' --output hello.wav` で再生可能な WAV ファイルが返却される

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] [US1] Contract test for POST /api/tts/synthesize in backend/tests/contract/test_tts_contract.py
- [x] T005 [P] [US1] Unit test for TTSService validation in backend/tests/unit/test_tts_service.py
- [x] T006 [P] [US1] Integration test for synthesize endpoint in backend/tests/integration/test_tts_api.py

### Implementation for User Story 1

- [x] T007 [P] [US1] Create TTSSynthesisRequest model in backend/src/models/tts.py
- [x] T008 [P] [US1] Create TTSErrorResponse and TTSErrorCode enum in backend/src/models/tts.py
- [x] T009 [US1] Implement TTSService with Style-Bert-VITS2 integration in backend/src/services/tts_service.py (depends on T007, T008)
- [x] T010 [US1] Add BERT model loading at service initialization in backend/src/services/tts_service.py
- [x] T011 [US1] Implement synthesize() method with text validation in backend/src/services/tts_service.py
- [x] T012 [US1] Add concurrency control with asyncio.Semaphore in backend/src/services/tts_service.py
- [x] T013 [US1] Implement POST /api/tts/synthesize endpoint in backend/src/api/tts.py (depends on T009-T012)
- [x] T014 [US1] Add WAV response with X-Processing-Time, X-Audio-Length, X-Sample-Rate headers in backend/src/api/tts.py
- [x] T015 [US1] Register TTS router in backend/src/main.py
- [x] T016 [US1] Add error handling for empty text, text too long, synthesis failure in backend/src/api/tts.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - 音声パラメータのカスタマイズ (Priority: P2)

**Goal**: 話速パラメータ (0.5-2.0) を指定して音声生成をカスタマイズ

**Independent Test**: `curl -X POST "http://localhost:8000/api/tts/synthesize" -H "Content-Type: application/json" -d '{"text": "早口で話します", "speed": 1.5}'` で速い音声が返却される

### Tests for User Story 2

- [x] T017 [P] [US2] Unit test for speed parameter validation in backend/tests/unit/test_tts_service.py
- [x] T018 [P] [US2] Integration test for speed parameter in backend/tests/integration/test_tts_api.py

### Implementation for User Story 2

- [x] T019 [US2] Add speed field to TTSSynthesisRequest model in backend/src/models/tts.py
- [x] T020 [US2] Update synthesize() to pass length parameter (speed -> 1/length conversion) in backend/src/services/tts_service.py
- [x] T021 [US2] Add INVALID_SPEED error handling in backend/src/api/tts.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - サービス健全性の確認 (Priority: P3)

**Goal**: サービスの稼働状況とモデル読み込み状態を確認

**Independent Test**: `curl "http://localhost:8000/api/tts/status"` で正常ステータスとモデル情報が返却される

### Tests for User Story 3

- [x] T022 [P] [US3] Contract test for GET /api/tts/status in backend/tests/contract/test_tts_contract.py
- [x] T023 [P] [US3] Unit test for get_status() in backend/tests/unit/test_tts_service.py
- [x] T024 [P] [US3] Integration test for status endpoint in backend/tests/integration/test_tts_api.py

### Implementation for User Story 3

- [x] T025 [P] [US3] Create TTSStatus and TTSHealthStatus enum in backend/src/models/tts.py
- [x] T026 [US3] Implement get_status() method in backend/src/services/tts_service.py
- [x] T027 [US3] Implement GET /api/tts/status endpoint in backend/src/api/tts.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T028 [P] Add processing time logging for observability in backend/src/services/tts_service.py
- [x] T029 [P] Add MODEL_NOT_LOADED and SERVICE_BUSY error responses in backend/src/api/tts.py
- [ ] T030 Run quickstart.md validation with manual curl tests (requires model files)
- [x] T031 Run full test suite with uv run pytest
- [x] T032 Run linting and type checking with uv run ruff check && uv run mypy

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - minimal blocking tasks
- **User Stories (Phase 3+)**: All depend on Setup phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup (Phase 1) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 models and service being complete (extends TTSSynthesisRequest)
- **User Story 3 (P3)**: Depends on US1 service being complete (queries TTSService state)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- T007 and T008 can run in parallel (different model classes)
- T004, T005, T006 can run in parallel (different test files)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /api/tts/synthesize in backend/tests/contract/test_tts_contract.py"
Task: "Unit test for TTSService validation in backend/tests/unit/test_tts_service.py"
Task: "Integration test for synthesize endpoint in backend/tests/integration/test_tts_api.py"

# Launch all models for User Story 1 together:
Task: "Create TTSSynthesisRequest model in backend/src/models/tts.py"
Task: "Create TTSErrorResponse and TTSErrorCode enum in backend/src/models/tts.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 3: User Story 1
3. **STOP and VALIDATE**: Test User Story 1 independently with curl
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup → Dependencies installed
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Speed parameter works
4. Add User Story 3 → Test independently → Status endpoint available
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup together
2. Once Setup is done:
   - Developer A: User Story 1 (blocking for US2, US3)
   - After US1 complete:
     - Developer B: User Story 2
     - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Style-Bert-VITS2 model files must be pre-downloaded before running tests
- Mock TTSModel.infer() for unit tests to avoid model loading
