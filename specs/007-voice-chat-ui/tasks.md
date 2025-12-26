# Tasks: Voice Chat Web UI

**Input**: Design documents from `/specs/007-voice-chat-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/frontend-api.ts, quickstart.md

**Tests**: TDD approach specified in constitution (Principle IV). Tests are written first for each component.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` (Next.js App Router)
- **Tests**: `frontend/tests/` (Jest + React Testing Library)
- **Backend**: Existing, no modifications needed

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, types, and API client setup

- [x] T001 Define TypeScript types for conversation state in frontend/src/types/conversation.ts
- [x] T002 [P] Define TypeScript types for audio state in frontend/src/types/audio.ts
- [x] T003 [P] Extend API client with conversation endpoints in frontend/src/lib/api.ts
- [x] T004 [P] Extend API client with orchestrator endpoint in frontend/src/lib/api.ts
- [x] T005 [P] Extend API client with TTS synthesize endpoint in frontend/src/lib/api.ts
- [x] T006 Create audio utility functions in frontend/src/lib/audio.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create ChatContext provider with reducer in frontend/src/components/providers/ChatContext.tsx
- [x] T008 [P] Create AudioContext provider with reducer in frontend/src/components/providers/AudioContext.tsx
- [x] T009 Update root layout to wrap providers in frontend/src/app/layout.tsx
- [x] T010 Create base ChatArea container component in frontend/src/components/chat/ChatArea.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Voice Conversation (Priority: P1) 🎯 MVP

**Goal**: Users can have a voice conversation with the assistant - speak a message, hear the response

**Independent Test**: Click microphone button, speak "こんにちは", hear assistant's response played through speakers

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US1] Test useVoiceRecorder hook in frontend/tests/hooks/useVoiceRecorder.test.ts
- [x] T012 [P] [US1] Test useAudioPlayer hook in frontend/tests/hooks/useAudioPlayer.test.ts
- [x] T013 [P] [US1] Test VoiceButton component in frontend/tests/components/voice/VoiceButton.test.tsx
- [x] T014 [P] [US1] Test AudioPlayer component in frontend/tests/components/voice/AudioPlayer.test.tsx

### Implementation for User Story 1

- [x] T015 [US1] Implement useVoiceRecorder hook (MediaRecorder API) in frontend/src/hooks/useVoiceRecorder.ts
- [x] T016 [US1] Implement useAudioPlayer hook (HTML5 Audio) in frontend/src/hooks/useAudioPlayer.ts
- [x] T017 [US1] Create VoiceButton component (toggle recording) in frontend/src/components/voice/VoiceButton.tsx
- [x] T018 [US1] Create AudioPlayer component (auto-play response) in frontend/src/components/voice/AudioPlayer.tsx
- [x] T019 [US1] Integrate voice input/output in ChatArea (send to orchestrator, play response) in frontend/src/components/chat/ChatArea.tsx
- [x] T020 [US1] Add recording indicator and stop controls to VoiceButton in frontend/src/components/voice/VoiceButton.tsx
- [x] T021 [US1] Add error handling for microphone permission denied in frontend/src/hooks/useVoiceRecorder.ts
- [x] T022 [US1] Add loading indicators during voice processing in frontend/src/components/chat/ChatArea.tsx

**Checkpoint**: At this point, users can speak and hear responses - MVP voice functionality complete

---

## Phase 4: User Story 2 - Conversation History Display (Priority: P1)

**Goal**: Users can see conversation history in a ChatGPT-like interface with sidebar navigation

**Independent Test**: Send multiple messages, see them in chat area; reload page, see conversations in sidebar

### Tests for User Story 2

- [ ] T023 [P] [US2] Test useConversations hook in frontend/tests/hooks/useConversations.test.ts
- [ ] T024 [P] [US2] Test useChat hook in frontend/tests/hooks/useChat.test.ts
- [ ] T025 [P] [US2] Test MessageBubble component in frontend/tests/components/chat/MessageBubble.test.tsx
- [ ] T026 [P] [US2] Test MessageList component in frontend/tests/components/chat/MessageList.test.tsx
- [ ] T027 [P] [US2] Test ConversationList component in frontend/tests/components/sidebar/ConversationList.test.tsx
- [ ] T028 [P] [US2] Test Sidebar component in frontend/tests/components/sidebar/Sidebar.test.tsx

### Implementation for User Story 2

- [ ] T029 [US2] Implement useConversations hook (fetch list, select) in frontend/src/hooks/useConversations.ts
- [ ] T030 [US2] Implement useChat hook (messages, send, receive) in frontend/src/hooks/useChat.ts
- [ ] T031 [P] [US2] Create MessageBubble component (user/assistant styling) in frontend/src/components/chat/MessageBubble.tsx
- [ ] T032 [US2] Create MessageList component (scrollable, auto-scroll) in frontend/src/components/chat/MessageList.tsx
- [ ] T033 [P] [US2] Create ConversationList component (list items, select) in frontend/src/components/sidebar/ConversationList.tsx
- [ ] T034 [US2] Create Sidebar component (mobile responsive, toggle) in frontend/src/components/sidebar/Sidebar.tsx
- [ ] T035 [US2] Integrate sidebar and message display in main page in frontend/src/app/page.tsx
- [ ] T036 [US2] Add loading state while fetching conversation history in frontend/src/components/sidebar/ConversationList.tsx
- [ ] T037 [US2] Style messages with user on right (blue) and assistant on left (gray) in frontend/src/components/chat/MessageBubble.tsx

**Checkpoint**: Users can see chat history and navigate past conversations - History display complete

---

## Phase 5: User Story 3 - Text Input Alternative (Priority: P2)

**Goal**: Users can type messages as an alternative to voice input

**Independent Test**: Type a message, press Enter or click send, see message in chat and hear response

### Tests for User Story 3

- [ ] T038 [P] [US3] Test InputArea component in frontend/tests/components/chat/InputArea.test.tsx

### Implementation for User Story 3

- [ ] T039 [US3] Create InputArea component (text field, send button) in frontend/src/components/chat/InputArea.tsx
- [ ] T040 [US3] Handle Enter key to send message in frontend/src/components/chat/InputArea.tsx
- [ ] T041 [US3] Integrate InputArea with chat flow (send text, receive response) in frontend/src/components/chat/ChatArea.tsx
- [ ] T042 [US3] Preserve typed text while voice recording is active in frontend/src/components/chat/InputArea.tsx

**Checkpoint**: Users can type messages - Text input alternative complete

---

## Phase 6: User Story 4 - New Conversation (Priority: P2)

**Goal**: Users can start a new conversation without previous context

**Independent Test**: Click "New Chat" button, chat area clears, send message, new conversation appears in sidebar

### Tests for User Story 4

- [ ] T043 [P] [US4] Test New Chat button functionality in frontend/tests/components/sidebar/Sidebar.test.tsx

### Implementation for User Story 4

- [ ] T044 [US4] Add "New Chat" button to Sidebar in frontend/src/components/sidebar/Sidebar.tsx
- [ ] T045 [US4] Implement new conversation creation in ChatContext in frontend/src/components/providers/ChatContext.tsx
- [ ] T046 [US4] Clear chat area and reset state on new conversation in frontend/src/components/chat/ChatArea.tsx
- [ ] T047 [US4] Update conversation list when new conversation is saved in frontend/src/hooks/useConversations.ts

**Checkpoint**: Users can start fresh conversations - New conversation feature complete

---

## Phase 7: User Story 5 - Audio Playback Control (Priority: P3)

**Goal**: Users can replay assistant responses and control auto-play with mute toggle

**Independent Test**: Click replay button on message to hear it again; toggle mute, new responses don't auto-play

### Tests for User Story 5

- [ ] T048 [P] [US5] Test MuteToggle component in frontend/tests/components/voice/MuteToggle.test.tsx
- [ ] T049 [P] [US5] Test replay button functionality in frontend/tests/components/chat/MessageBubble.test.tsx

### Implementation for User Story 5

- [ ] T050 [US5] Create MuteToggle component in frontend/src/components/voice/MuteToggle.tsx
- [ ] T051 [US5] Add replay button to assistant MessageBubble (re-request TTS) in frontend/src/components/chat/MessageBubble.tsx
- [ ] T052 [US5] Integrate mute state with audio auto-play in AudioContext in frontend/src/components/providers/AudioContext.tsx
- [ ] T053 [US5] Add MuteToggle to header or controls area in frontend/src/app/page.tsx
- [ ] T054 [US5] Implement TTS re-request for replay in useAudioPlayer in frontend/src/hooks/useAudioPlayer.ts

**Checkpoint**: Users have full audio control - Audio playback controls complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T055 [P] Add responsive design for mobile (sidebar collapse) in frontend/src/components/sidebar/Sidebar.tsx
- [ ] T056 [P] Add keyboard shortcuts (Escape to cancel recording) in frontend/src/hooks/useVoiceRecorder.ts
- [ ] T057 [P] Improve error messages for all error scenarios in frontend/src/lib/api.ts
- [ ] T058 Add conversation deletion capability in frontend/src/components/sidebar/ConversationList.tsx
- [ ] T059 [P] Add timestamp display to messages in frontend/src/components/chat/MessageBubble.tsx
- [ ] T060 Run quickstart.md manual testing checklist
- [ ] T061 Run npm test to verify all tests pass
- [ ] T062 Run npm run lint to ensure code quality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Voice MVP
- **User Story 2 (Phase 4)**: Depends on Foundational - Can run parallel to US1
- **User Story 3 (Phase 5)**: Depends on Foundational - Can run parallel to US1/US2
- **User Story 4 (Phase 6)**: Depends on US2 (Sidebar) - Needs sidebar to add button
- **User Story 5 (Phase 7)**: Depends on US1 (AudioPlayer) and US2 (MessageBubble) - Extends existing components
- **Polish (Phase 8)**: Depends on all user stories being complete

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
          ┌──────────────────┼──────────────────┐
          │                  │                  │
┌─────────▼─────────┐ ┌──────▼──────┐ ┌────────▼────────┐
│ US1: Voice (P1) 🎯│ │US2: History │ │US3: Text Input  │
│      MVP          │ │   (P1)      │ │     (P2)        │
└─────────┬─────────┘ └──────┬──────┘ └─────────────────┘
          │                  │
          │           ┌──────▼──────┐
          │           │US4: New Chat│
          │           │    (P2)     │
          │           └─────────────┘
          │
┌─────────▼─────────┐
│US5: Audio Control │
│      (P3)         │
└───────────────────┘
```

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Hooks before components
3. Components before integration
4. Core implementation before polish
5. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T001, T002 can run in parallel (different type files)
- T003, T004, T005 can run in parallel (different API endpoints in same file, but independent)
- T006 depends on T002 (audio types)

**Phase 2 (Foundational)**:
- T007, T008 can run in parallel (different context providers)
- T009, T010 depend on T007, T008

**User Story 1 (Voice)**:
- T011, T012, T013, T014 can run in parallel (different test files)
- T015, T016 depend on tests passing
- T017, T018 depend on T015, T016 respectively

**User Story 2 (History)**:
- T023, T024, T025, T026, T027, T028 can run in parallel (different test files)
- T031, T033 can run in parallel (different components)
- T029, T030 can run in parallel (different hooks)

**User Story 3, 4, 5**:
- Test tasks within each story can run in parallel
- Implementation follows test completion

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Test useVoiceRecorder hook in frontend/tests/hooks/useVoiceRecorder.test.ts"
Task: "Test useAudioPlayer hook in frontend/tests/hooks/useAudioPlayer.test.ts"
Task: "Test VoiceButton component in frontend/tests/components/voice/VoiceButton.test.tsx"
Task: "Test AudioPlayer component in frontend/tests/components/voice/AudioPlayer.test.tsx"

# After tests fail, implement hooks in parallel:
Task: "Implement useVoiceRecorder hook in frontend/src/hooks/useVoiceRecorder.ts"
Task: "Implement useAudioPlayer hook in frontend/src/hooks/useAudioPlayer.ts"

# Then implement components:
Task: "Create VoiceButton component in frontend/src/components/voice/VoiceButton.tsx"
Task: "Create AudioPlayer component in frontend/src/components/voice/AudioPlayer.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T010)
3. Complete Phase 3: User Story 1 - Voice Conversation (T011-T022)
4. **STOP and VALIDATE**: Test voice input/output manually
5. Deploy/demo if ready - users can speak and hear responses

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. **Add User Story 1** → Voice MVP → Deploy/Demo
3. **Add User Story 2** → History Display → Deploy/Demo
4. **Add User Story 3** → Text Input → Deploy/Demo
5. **Add User Story 4** → New Conversation → Deploy/Demo
6. **Add User Story 5** → Audio Controls → Deploy/Demo
7. Polish → Final release

### Suggested MVP Scope

**MVP = User Story 1 (Voice Conversation)**

This delivers the core value proposition:
- Speak to the assistant
- Hear the response
- Basic chat display (single conversation)

User can interact hands-free immediately. History, text input, and advanced controls come later.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend APIs are existing and require no modifications
- Audio format: WebM/Opus for recording, WAV for playback (backend converts)
- No audio caching: replay re-requests from TTS endpoint
