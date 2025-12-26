# Tasks: リアルタイム WebSocket 通信

**Input**: Design documents from `/specs/008-realtime-websocket/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD approach specified in constitution (Principle IV). Tests are written first for each component.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` (FastAPI)
- **Frontend**: `frontend/src/` (Next.js)
- **Backend Tests**: `backend/tests/`
- **Frontend Tests**: `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Types, models, and shared utilities for WebSocket communication

- [x] T001 Copy WebSocket message models from contracts to backend/src/models/websocket.py
- [x] T002 [P] Copy WebSocket types from contracts to frontend/src/types/websocket.ts
- [x] T003 [P] Add deepgram-sdk dependency to backend/pyproject.toml
- [x] T004 [P] Create WebSocket configuration in backend/src/config.py (env vars for STT service)
- [x] T005 Create WebSocket client utility in frontend/src/lib/websocket.ts (connection helper, message serialization)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core WebSocket infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create ConnectionManager class in backend/src/lib/websocket_manager.py
- [x] T007 [P] Create base WebSocket endpoint skeleton in backend/src/api/websocket.py
- [x] T008 [P] Register WebSocket endpoint in backend/src/main.py
- [x] T009 Create useWebSocket hook with connection/reconnection logic in frontend/src/hooks/useWebSocket.ts
- [x] T010 [P] Create WebSocketProvider context in frontend/src/components/providers/WebSocketContext.tsx
- [x] T011 Update root layout to wrap WebSocketProvider in frontend/src/app/layout.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - リアルタイム文字起こし表示 (Priority: P1)

**Goal**: Users see their speech transcribed in real-time as they speak

**Independent Test**: Click microphone, speak, see partial transcript updating character-by-character, then final transcript appears

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Test StreamingSTTService in backend/tests/unit/test_streaming_stt.py
- [ ] T013 [P] [US1] Test WebSocket transcript messages in backend/tests/integration/test_websocket_transcript.py
- [ ] T014 [P] [US1] Test useRealtimeTranscript hook in frontend/tests/hooks/useRealtimeTranscript.test.ts
- [ ] T015 [P] [US1] Test RealtimeTranscript component in frontend/tests/components/RealtimeTranscript.test.tsx

### Implementation for User Story 1

- [ ] T016 [US1] Implement StreamingSTTService adapter for Deepgram in backend/src/services/streaming_stt.py
- [ ] T017 [US1] Add audio_chunk/audio_end handlers to WebSocket endpoint in backend/src/api/websocket.py
- [ ] T018 [US1] Implement transcript_partial/transcript_final message sending in backend/src/api/websocket.py
- [ ] T019 [US1] Create useRealtimeTranscript hook (partial/final state) in frontend/src/hooks/useRealtimeTranscript.ts
- [ ] T020 [US1] Create RealtimeTranscript component (displays updating text) in frontend/src/components/chat/RealtimeTranscript.tsx
- [ ] T021 [US1] Modify useVoiceRecorder to stream audio chunks via WebSocket in frontend/src/hooks/useVoiceRecorder.ts
- [ ] T022 [US1] Integrate RealtimeTranscript with ChatArea in frontend/src/components/chat/ChatArea.tsx
- [ ] T023 [US1] Add smooth text animation (no flickering) to RealtimeTranscript in frontend/src/components/chat/RealtimeTranscript.tsx

**Checkpoint**: At this point, users can speak and see real-time transcription - Core P1 feature complete

---

## Phase 4: User Story 2 - 処理状況のリアルタイム表示 (Priority: P2)

**Goal**: Users see status indicators (transcribing, generating, synthesizing) as the system processes

**Independent Test**: After speaking, see status change from "Transcribing..." to "Generating..." to "Synthesizing..." to "Ready"

### Tests for User Story 2

- [ ] T024 [P] [US2] Test status_update message handling in backend/tests/unit/test_websocket_status.py
- [ ] T025 [P] [US2] Test useProcessingStatus hook in frontend/tests/hooks/useProcessingStatus.test.ts
- [ ] T026 [P] [US2] Test ProcessingStatus component in frontend/tests/components/ProcessingStatus.test.tsx

### Implementation for User Story 2

- [ ] T027 [US2] Add status_update message emission at each processing stage in backend/src/api/websocket.py
- [ ] T028 [US2] Create useProcessingStatus hook (status state machine) in frontend/src/hooks/useProcessingStatus.ts
- [ ] T029 [US2] Create ProcessingStatus component (status indicator UI) in frontend/src/components/chat/ProcessingStatus.tsx
- [ ] T030 [US2] Integrate ProcessingStatus with ChatArea in frontend/src/components/chat/ChatArea.tsx
- [ ] T031 [US2] Add Japanese status labels (文字起こし中、応答生成中、音声合成中) in frontend/src/components/chat/ProcessingStatus.tsx

**Checkpoint**: Users see processing status updates - Status display feature complete

---

## Phase 5: User Story 3 - 応答テキストのストリーミング表示 (Priority: P2)

**Goal**: LLM response appears character-by-character as it's generated (ChatGPT-like streaming)

**Independent Test**: After user input, see AI response text appearing incrementally, not all at once

### Tests for User Story 3

- [ ] T032 [P] [US3] Test StreamingLLMService in backend/tests/unit/test_streaming_llm.py
- [ ] T033 [P] [US3] Test response_chunk/response_complete messages in backend/tests/integration/test_websocket_response.py
- [ ] T034 [P] [US3] Test streaming response display in frontend/tests/components/StreamingResponse.test.tsx

### Implementation for User Story 3

- [ ] T035 [US3] Create StreamingLLMService (forwards OpenAI stream to WebSocket) in backend/src/services/streaming_llm.py
- [ ] T036 [US3] Add response_chunk message emission during LLM streaming in backend/src/api/websocket.py
- [ ] T037 [US3] Add response_complete message emission after LLM finishes in backend/src/api/websocket.py
- [ ] T038 [US3] Update useProcessingStatus to accumulate streaming response text in frontend/src/hooks/useProcessingStatus.ts
- [ ] T039 [US3] Create StreamingResponse component (accumulating text display) in frontend/src/components/chat/StreamingResponse.tsx
- [ ] T040 [US3] Integrate streaming response with MessageBubble in frontend/src/components/chat/MessageBubble.tsx
- [ ] T041 [US3] Trigger TTS after response_complete received in frontend/src/components/chat/ChatArea.tsx

**Checkpoint**: AI responses stream in real-time - Response streaming feature complete

---

## Phase 6: User Story 4 - 接続状態の可視化 (Priority: P3)

**Goal**: Users see WebSocket connection status (connected/reconnecting/disconnected) indicator

**Independent Test**: Disconnect network, see indicator turn red, reconnect, see it turn green

### Tests for User Story 4

- [ ] T042 [P] [US4] Test reconnection logic in useWebSocket in frontend/tests/hooks/useWebSocket.test.ts
- [ ] T043 [P] [US4] Test ConnectionIndicator component in frontend/tests/components/ConnectionIndicator.test.tsx

### Implementation for User Story 4

- [ ] T044 [US4] Add exponential backoff reconnection to useWebSocket in frontend/src/hooks/useWebSocket.ts
- [ ] T045 [US4] Create ConnectionIndicator component (colored dot with tooltip) in frontend/src/components/status/ConnectionIndicator.tsx
- [ ] T046 [US4] Add ConnectionIndicator to page header in frontend/src/app/page.tsx
- [ ] T047 [US4] Implement connection_ack handler and session management in frontend/src/hooks/useWebSocket.ts
- [ ] T048 [US4] Add ping/pong heartbeat handling in frontend/src/hooks/useWebSocket.ts and backend/src/api/websocket.py

**Checkpoint**: Connection status is visible - Connection indicator feature complete

---

## Phase 7: HTTP Fallback & Error Handling

**Purpose**: Graceful degradation for WebSocket-incompatible environments

- [ ] T049 [P] Add WebSocket availability check in frontend/src/lib/websocket.ts
- [ ] T050 Create HTTP fallback mode using existing orchestrator API in frontend/src/hooks/useWebSocket.ts
- [ ] T051 [P] Add error message handling for all WebSocketErrorCode cases in frontend/src/components/chat/ChatArea.tsx
- [ ] T052 Add recoverable error retry UI in frontend/src/components/chat/ErrorRetry.tsx
- [ ] T053 Implement cancel message handling (abort ongoing STT/LLM) in backend/src/api/websocket.py

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T054 [P] Add WebSocket debug logging in development mode in backend/src/api/websocket.py
- [ ] T055 [P] Add client-side debug logging in development mode in frontend/src/hooks/useWebSocket.ts
- [ ] T056 [P] Add metrics/timing to WebSocket messages in backend/src/api/websocket.py
- [ ] T057 Performance test: verify <1 second for first transcript display
- [ ] T058 Performance test: verify <500ms for status update display
- [ ] T059 Run quickstart.md manual testing checklist
- [ ] T060 Run backend tests (uv run pytest)
- [ ] T061 Run frontend tests (npm test)
- [ ] T062 Run backend lint (uv run ruff check .)
- [ ] T063 Run frontend lint (npm run lint)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Core real-time functionality
- **User Story 2 (Phase 4)**: Depends on Foundational - Can run parallel to US1
- **User Story 3 (Phase 5)**: Depends on Foundational + partial US1 (WebSocket flow) - Can start after US1 T018
- **User Story 4 (Phase 6)**: Depends on Foundational only - Can run parallel to all stories
- **HTTP Fallback (Phase 7)**: Depends on all user stories complete
- **Polish (Phase 8)**: Depends on all features being complete

### User Story Dependencies

```text
                    ┌─────────────────┐
                    │  Phase 1: Setup │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Phase 2: Found. │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┬─────────────────┐
          │                  │                  │                 │
┌─────────▼─────────┐ ┌──────▼──────┐ ┌────────▼────────┐ ┌──────▼──────┐
│ US1: Transcript   │ │US2: Status  │ │US3: Response    │ │US4: Connect │
│   (P1) 🎯 MVP    │ │   (P2)      │ │  Streaming (P2) │ │  Status (P3)│
└─────────┬─────────┘ └──────┬──────┘ └────────┬────────┘ └──────┬──────┘
          │                  │                 │                 │
          └──────────────────┴────────┬────────┴─────────────────┘
                                      │
                             ┌────────▼────────┐
                             │ Phase 7: HTTP   │
                             │   Fallback      │
                             └────────┬────────┘
                                      │
                             ┌────────▼────────┐
                             │ Phase 8: Polish │
                             └─────────────────┘
```

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Backend models before services
3. Backend services before API handlers
4. Frontend hooks before components
5. Components before integration
6. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T001, T002, T003, T004 can run in parallel (different files)
- T005 depends on T002 (uses types)

**Phase 2 (Foundational)**:
- T006, T007, T008 can run in parallel (backend)
- T009, T010 can run in parallel (frontend)
- T011 depends on T010

**User Stories**:
- All test tasks within each story marked [P] can run in parallel
- US1, US2, US3, US4 can be worked on by different team members after Foundational

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Test StreamingSTTService in backend/tests/unit/test_streaming_stt.py"
Task: "Test WebSocket transcript messages in backend/tests/integration/test_websocket_transcript.py"
Task: "Test useRealtimeTranscript hook in frontend/tests/hooks/useRealtimeTranscript.test.ts"
Task: "Test RealtimeTranscript component in frontend/tests/components/RealtimeTranscript.test.tsx"

# After tests fail, implement backend in sequence:
Task: "Implement StreamingSTTService adapter in backend/src/services/streaming_stt.py"
Task: "Add audio_chunk/audio_end handlers in backend/src/api/websocket.py"
Task: "Implement transcript message sending in backend/src/api/websocket.py"

# Then implement frontend (can overlap with backend):
Task: "Create useRealtimeTranscript hook in frontend/src/hooks/useRealtimeTranscript.ts"
Task: "Create RealtimeTranscript component in frontend/src/components/chat/RealtimeTranscript.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T011)
3. Complete Phase 3: User Story 1 - Real-time Transcript (T012-T023)
4. **STOP and VALIDATE**: Test real-time transcription manually
5. Deploy/demo if ready - users can speak and see real-time text

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. **Add User Story 1** → Real-time transcript → Deploy/Demo (MVP)
3. **Add User Story 2** → Status display → Deploy/Demo
4. **Add User Story 3** → Response streaming → Deploy/Demo
5. **Add User Story 4** → Connection indicator → Deploy/Demo
6. HTTP Fallback → Robustness complete
7. Polish → Final release

### Suggested MVP Scope

**MVP = User Story 1 (Real-time Transcript)**

This delivers the core value proposition:
- Speak and see text appear in real-time
- Confirmation that the system "hears" the user
- Immediate feedback during voice input

This is the most impactful feature for reducing perceived latency.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend uses Deepgram for streaming STT (WebSocket-native)
- Frontend uses native WebSocket API (no external dependencies)
- Existing HTTP APIs remain unchanged for backward compatibility
