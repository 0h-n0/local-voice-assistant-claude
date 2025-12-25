# Tasks: STT API - Japanese Speech-to-Text

**Input**: Design documents from `/specs/002-stt-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Constitution IV (TDD) - write tests first, ensure they fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (backend extension)**: `backend/src/`, `backend/tests/`
- Following existing structure from 001-project-setup

---

## Phase 1: Setup (Project Dependencies)

**Purpose**: Add required dependencies for STT functionality

- [x] T001 Add STT dependencies to backend/pyproject.toml (reazonspeech, pydub, soundfile, python-multipart)
- [x] T002 Run `uv sync` to install dependencies and verify installation
- [x] T003 Verify ffmpeg is available in system (required for pydub audio conversion)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Pydantic models in backend/src/models/stt.py (TranscriptionResponse, Segment, STTStatus, StreamMessage, ErrorResponse, ErrorCode enum)
- [x] T005 Create STTService skeleton in backend/src/services/stt_service.py (class with load_model, transcribe, get_status methods)
- [x] T006 Add STT router registration in backend/src/main.py (import and include stt router with lifespan for model loading)
- [x] T007 Create empty backend/src/api/stt.py with router definition

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Audio File Transcription API (Priority: P1) MVP

**Goal**: Upload audio file (WAV, MP3, FLAC, OGG) via POST and receive transcribed Japanese text

**Independent Test**: `curl -X POST -F "file=@test.wav" http://localhost:8000/api/stt/transcribe` returns JSON with transcribed text

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Contract test for POST /api/stt/transcribe in backend/tests/contract/test_stt_transcribe.py
- [x] T009 [P] [US1] Unit test for audio format validation in backend/tests/unit/test_stt_service.py
- [x] T010 [P] [US1] Unit test for audio resampling to 16kHz in backend/tests/unit/test_stt_service.py

### Implementation for User Story 1

- [x] T011 [US1] Implement audio format validation in STTService (check extension, validate file content)
- [x] T012 [US1] Implement audio conversion to WAV 16kHz using pydub in STTService
- [x] T013 [US1] Implement model loading with reazonspeech.nemo.asr.load_model() in STTService
- [x] T014 [US1] Implement transcribe method using reazonspeech.nemo.asr.transcribe() in STTService
- [x] T015 [US1] Implement POST /api/stt/transcribe endpoint in backend/src/api/stt.py (file upload, validation, transcription)
- [x] T016 [US1] Add file size validation (max 100MB) with FILE_TOO_LARGE error
- [x] T017 [US1] Add error handling for UNSUPPORTED_FORMAT, EMPTY_AUDIO, PROCESSING_ERROR
- [x] T018 [US1] Implement asyncio.Semaphore for concurrent request limiting (max 3)
- [x] T019 [US1] Run contract and unit tests - verify all pass

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Real-time WebSocket Streaming (Priority: P2)

**Goal**: WebSocket endpoint for real-time audio streaming with progressive transcription results

**Independent Test**: WebSocket client sends audio chunks and receives partial/final transcription messages

### Tests for User Story 2

- [x] T020 [P] [US2] Contract test for WebSocket /api/stt/stream in backend/tests/contract/test_stt_stream.py
- [x] T021 [P] [US2] Unit test for audio buffer management in backend/tests/unit/test_stt_service.py

### Implementation for User Story 2

- [x] T022 [US2] Create AudioBuffer class in backend/src/services/stt_service.py (buffer chunks, detect silence, should_process logic)
- [x] T023 [US2] Implement WebSocket endpoint in backend/src/api/stt.py (/api/stt/stream)
- [x] T024 [US2] Implement WebSocket message handling (receive bytes, buffer, process, send StreamMessage)
- [x] T025 [US2] Add connection lifecycle management (accept, error handling, cleanup on disconnect)
- [x] T026 [US2] Run WebSocket tests - verify all pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Model Health and Status API (Priority: P3)

**Goal**: Endpoint to check STT model status, device info, and memory usage

**Independent Test**: `curl http://localhost:8000/api/stt/status` returns JSON with model_loaded, device, memory_usage_mb

### Tests for User Story 3

- [x] T027 [P] [US3] Contract test for GET /api/stt/status in backend/tests/contract/test_stt_status.py

### Implementation for User Story 3

- [x] T028 [US3] Implement get_status method in STTService (check model loaded, get device, calculate memory usage)
- [x] T029 [US3] Implement GET /api/stt/status endpoint in backend/src/api/stt.py
- [x] T030 [US3] Add MODEL_NOT_LOADED error handling (503 if model still loading)
- [x] T031 [US3] Run status endpoint tests - verify all pass

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T032 Add logging for all STT operations (request received, processing time, errors)
- [x] T033 Run all tests together (`uv run pytest backend/tests/`)
- [x] T034 Run linting and type checking (`uv run ruff check`, `uv run mypy`)
- [x] T035 [P] Run quickstart.md validation - test all documented curl commands
- [x] T036 Update backend/src/main.py CORS settings if needed for frontend integration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3)
  - Or in parallel if staffed
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Phase 2 - Uses same STTService, independent of US1 endpoints
- **User Story 3 (P3)**: Can start after Phase 2 - Uses same STTService, independent of other endpoints

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Service methods before API endpoints
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 2 (Foundational)**:
- T004, T005, T006, T007 can run in parallel (different files)

**Phase 3 (US1)**:
- T008, T009, T010 tests can run in parallel
- After tests: T011-T14 are sequential (build on each other)

**Phase 4 (US2)**:
- T020, T021 tests can run in parallel

**Phase 5 (US3)**:
- T027 is single test, then implementation

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /api/stt/transcribe in backend/tests/contract/test_stt_transcribe.py"
Task: "Unit test for audio format validation in backend/tests/unit/test_stt_service.py"
Task: "Unit test for audio resampling to 16kHz in backend/tests/unit/test_stt_service.py"

# Then sequential implementation:
Task: "Implement audio format validation in STTService"
Task: "Implement audio conversion to WAV 16kHz using pydub"
Task: "Implement model loading with reazonspeech"
Task: "Implement transcribe method"
Task: "Implement POST /api/stt/transcribe endpoint"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (dependencies)
2. Complete Phase 2: Foundational (models, service skeleton)
3. Complete Phase 3: User Story 1 (file transcription)
4. **STOP and VALIDATE**: Test with `curl -X POST -F "file=@test.wav" http://localhost:8000/api/stt/transcribe`
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP ready!
3. Add User Story 2 → WebSocket streaming available
4. Add User Story 3 → Status monitoring available
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Model loading happens once at startup via FastAPI lifespan
- GPU recommended but CPU fallback supported (slower)
