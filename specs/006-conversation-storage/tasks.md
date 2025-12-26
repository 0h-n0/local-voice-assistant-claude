# Tasks: Conversation History Storage

**Input**: Design documents from `/specs/006-conversation-storage/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Included per project constitution (TDD approach)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (backend-only)**: `backend/src/`, `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and database infrastructure

- [x] T001 Add aiosqlite dependency to backend/pyproject.toml
- [x] T002 [P] Create database directory structure backend/src/db/
- [x] T003 [P] Create Pydantic models for conversation in backend/src/models/conversation.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement database connection manager in backend/src/db/database.py (schema creation, WAL mode, foreign keys)
- [x] T005 Implement ConversationStorageService base class with initialization in backend/src/services/conversation_storage_service.py
- [x] T006 Add CONVERSATION_DB_PATH to backend/src/config.py
- [x] T007 [P] Register database lifecycle hooks (startup/shutdown) in backend/src/main.py
- [x] T008 [P] Create conversation storage service dependency in backend/src/dependencies.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Save Conversation Message (Priority: P1) MVP

**Goal**: Automatically save user and assistant messages when voice dialogue completes

**Independent Test**: Execute voice dialogue API once, verify conversation and messages exist in database

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Unit test for save_message method in backend/tests/unit/test_conversation_storage_service.py
- [x] T010 [P] [US1] Unit test for conversation auto-creation in backend/tests/unit/test_conversation_storage_service.py

### Implementation for User Story 1

- [x] T011 [US1] Implement save_message(conversation_id, role, content) method in backend/src/services/conversation_storage_service.py
- [x] T012 [US1] Implement auto-creation of conversation record when first message is saved in backend/src/services/conversation_storage_service.py
- [x] T013 [US1] Add conversation_id generation (UUID) to OrchestratorService in backend/src/services/orchestrator_service.py
- [x] T014 [US1] Inject ConversationStorageService into OrchestratorService in backend/src/services/orchestrator_service.py
- [x] T015 [US1] Call save_message for user and assistant messages after dialogue completion in backend/src/services/orchestrator_service.py
- [x] T016 [US1] Add structured logging for save operations in backend/src/services/conversation_storage_service.py

**Checkpoint**: User Story 1 complete - messages are automatically saved on voice dialogue

---

## Phase 4: User Story 2 - Retrieve Conversation History (Priority: P1)

**Goal**: Retrieve conversation history via REST API (list and detail endpoints)

**Independent Test**: Save messages via orchestrator, then GET /api/conversations and GET /api/conversations/{id} return correct data

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T017 [P] [US2] Contract test for GET /api/conversations in backend/tests/contract/test_conversation_contract.py
- [x] T018 [P] [US2] Contract test for GET /api/conversations/{id} in backend/tests/contract/test_conversation_contract.py
- [x] T019 [P] [US2] Integration test for list conversations endpoint in backend/tests/integration/test_conversation_api.py
- [x] T020 [P] [US2] Integration test for get conversation detail endpoint in backend/tests/integration/test_conversation_api.py

### Implementation for User Story 2

- [x] T021 [US2] Implement list_conversations(limit, offset) method in backend/src/services/conversation_storage_service.py
- [x] T022 [US2] Implement get_conversation(conversation_id) method in backend/src/services/conversation_storage_service.py
- [x] T023 [US2] Create conversations API router in backend/src/api/conversations.py
- [x] T024 [US2] Implement GET /api/conversations endpoint with pagination in backend/src/api/conversations.py
- [x] T025 [US2] Implement GET /api/conversations/{conversation_id} endpoint in backend/src/api/conversations.py
- [x] T026 [US2] Add ConversationNotFoundError exception handling (404) in backend/src/api/conversations.py
- [x] T027 [US2] Register conversations router in backend/src/main.py
- [x] T028 [US2] Add structured logging for retrieval operations in backend/src/services/conversation_storage_service.py

**Checkpoint**: User Story 2 complete - conversation history can be retrieved via API

---

## Phase 5: User Story 3 - Delete Conversation (Priority: P2)

**Goal**: Delete conversation and all related messages via REST API

**Independent Test**: Save a conversation, DELETE /api/conversations/{id}, then GET returns 404

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T029 [P] [US3] Contract test for DELETE /api/conversations/{id} in backend/tests/contract/test_conversation_contract.py
- [x] T030 [P] [US3] Integration test for delete conversation endpoint in backend/tests/integration/test_conversation_api.py

### Implementation for User Story 3

- [x] T031 [US3] Implement delete_conversation(conversation_id) method in backend/src/services/conversation_storage_service.py
- [x] T032 [US3] Implement DELETE /api/conversations/{conversation_id} endpoint in backend/src/api/conversations.py
- [x] T033 [US3] Verify cascade delete of messages via foreign key constraint in backend/tests/integration/test_conversation_api.py
- [x] T034 [US3] Add structured logging for delete operations in backend/src/services/conversation_storage_service.py

**Checkpoint**: User Story 3 complete - conversations can be deleted via API

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Performance validation, error handling, and cleanup

- [x] T035 [P] Validate save performance < 100ms in backend/tests/integration/test_conversation_api.py
- [x] T036 [P] Validate retrieval performance (100 messages) < 500ms in backend/tests/integration/test_conversation_api.py
- [x] T037 [P] Validate list performance (20 conversations) < 200ms in backend/tests/integration/test_conversation_api.py
- [x] T038 Add database error handling (503 response) in backend/src/api/conversations.py
- [x] T039 Run quickstart.md validation (manual curl commands)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 and US2 are both P1, but US2 depends on US1 for test data
  - US3 depends on save functionality for test data
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Uses US1 save for test data but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Uses US1 save for test data but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Service methods before API endpoints
- Core implementation before integration with orchestrator
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003 can run in parallel (Phase 1)
- T007, T008 can run in parallel (Phase 2)
- All test tasks within a story can run in parallel
- T035, T036, T037 can run in parallel (Phase 6)

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Contract test for GET /api/conversations in backend/tests/contract/test_conversation_contract.py"
Task: "Contract test for GET /api/conversations/{id} in backend/tests/contract/test_conversation_contract.py"
Task: "Integration test for list conversations endpoint in backend/tests/integration/test_conversation_api.py"
Task: "Integration test for get conversation detail endpoint in backend/tests/integration/test_conversation_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Save Messages)
4. Complete Phase 4: User Story 2 (Retrieve History)
5. **STOP and VALIDATE**: Test via curl commands from quickstart.md
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Messages are saved automatically
3. Add User Story 2 -> History can be retrieved via API (MVP!)
4. Add User Story 3 -> Deletion capability added
5. Complete Polish -> Performance validated

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Database uses WAL mode for concurrent read support
- Foreign key ON DELETE CASCADE handles message cleanup automatically
