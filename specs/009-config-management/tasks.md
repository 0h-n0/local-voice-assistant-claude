# Tasks: 設定管理機能

**Input**: Design documents from `/specs/009-config-management/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD approach per Constitution (Principle IV). Tests are written first for each component.

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

**Purpose**: Add pydantic-settings dependency and prepare project structure

- [x] T001 Add pydantic-settings dependency to backend/pyproject.toml
- [x] T002 [P] Create backend/src/models/config.py (empty module)
- [x] T003 [P] Create backend/.env.example with all configuration variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core settings infrastructure that MUST be complete before user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create base Settings class using pydantic-settings in backend/src/models/config.py
- [x] T005 Create TTSSettings model in backend/src/models/config.py
- [x] T006 [P] Create OrchestratorSettings model in backend/src/models/config.py
- [x] T007 [P] Create WebSocketSettings model in backend/src/models/config.py
- [x] T008 [P] Create StorageSettings model in backend/src/models/config.py
- [x] T009 Create global settings instance with .env loading in backend/src/models/config.py
- [x] T010 Add backward-compatible exports in backend/src/config.py (alias to new Settings)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 環境変数による設定管理 (Priority: P1)

**Goal**: 開発者が `.env` ファイルでAPIキーやサービスURLを管理できる

**Independent Test**: `.env` ファイルを作成し、アプリケーションを起動して設定値が正しく読み込まれることを確認

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US1] Test .env file loading in backend/tests/unit/test_config_loading.py
- [x] T012 [P] [US1] Test environment variable priority over .env in backend/tests/unit/test_config_priority.py
- [x] T013 [P] [US1] Test validation error on invalid values in backend/tests/unit/test_config_validation.py
- [x] T014 [P] [US1] Test SecretStr masking for API keys in backend/tests/unit/test_config_secrets.py

### Implementation for User Story 1

- [x] T015 [US1] Create DeepgramSettings model with SecretStr api_key in backend/src/models/config.py
- [x] T016 [US1] Create OpenAISettings model with SecretStr api_key in backend/src/models/config.py
- [x] T017 [US1] Integrate DeepgramSettings and OpenAISettings into root Settings class
- [x] T018 [US1] Update existing services to use new Settings (LLM, STT services)
- [x] T019 [US1] Add startup validation with clear error messages in backend/src/main.py
- [x] T020 [US1] Add configuration logging (with masked secrets) on startup

**Checkpoint**: At this point, users can manage API keys via .env file - Core P1 feature complete

---

## Phase 4: User Story 2 - モデルパスの設定 (Priority: P1)

**Goal**: 開発者がSTT/TTSモデルのパスを設定ファイルで管理できる

**Independent Test**: 設定ファイルでモデルパスを変更し、アプリケーションが指定されたモデルを読み込むことを確認

### Tests for User Story 2

- [x] T021 [P] [US2] Test model path configuration in backend/tests/unit/test_config_model_paths.py
- [x] T022 [P] [US2] Test path validation (existence check) in backend/tests/unit/test_config_path_validation.py

### Implementation for User Story 2

- [x] T023 [US2] Add path validation to TTSSettings (model_path existence) in backend/src/models/config.py
  - Note: Validation deferred to startup via validate_startup_config() for cleaner error messages
- [x] T024 [US2] Update TTS service to use Settings.tts.model_path in backend/src/services/tts.py
  - Note: Uses backward-compatible exports from src/config.py which source from Settings
- [x] T025 [US2] Add clear error message when model path doesn't exist
  - Note: Implemented in validate_startup_config() in main.py

**Checkpoint**: At this point, users can manage model paths via .env file - Model path feature complete

---

## Phase 5: User Story 3 - サービスURL設定 (Priority: P2)

**Goal**: 開発者が外部サービスのエンドポイントURLを設定で管理できる

**Independent Test**: 設定でサービスURLを変更し、アプリケーションが正しいエンドポイントに接続することを確認

### Tests for User Story 3

- [x] T026 [P] [US3] Test URL configuration in backend/tests/unit/test_config_urls.py
- [x] T027 [P] [US3] Test URL validation in backend/tests/unit/test_config_url_validation.py

### Implementation for User Story 3

- [x] T028 [US3] Add base_url field to OpenAISettings with URL validation in backend/src/models/config.py
  - Note: Already implemented with empty string default for compatibility
- [x] T029 [US3] Update LLM service to use Settings.openai.base_url in backend/src/services/llm.py
  - Note: LLM service now uses settings.openai.base_url with conditional logic
- [x] T030 [US3] Add URL format validation error messages
  - Note: Simple string validation; pydantic handles type validation

**Checkpoint**: At this point, users can manage service URLs via .env file - URL config feature complete

---

## Phase 6: User Story 4 - 設定の一覧表示 (Priority: P3)

**Goal**: 開発者が現在の設定値を確認できるAPIを利用できる

**Independent Test**: 設定確認APIを呼び出し、現在の設定値（機密情報はマスク）が表示されることを確認

### Tests for User Story 4

- [x] T031 [P] [US4] Test GET /api/config endpoint in backend/tests/unit/test_config_api.py
- [x] T032 [P] [US4] Test secret masking in API response in backend/tests/unit/test_config_api_secrets.py

### Implementation for User Story 4

- [x] T033 [US4] Create ConfigInfoResponse model in backend/src/models/config.py
  - Note: Implemented as get_safe_config() function returning dict
- [x] T034 [US4] Create config router with GET /api/config in backend/src/api/config.py
- [x] T035 [US4] Implement settings serialization with SecretStr masking
  - Note: API keys show "api_key_configured: true/false" instead of values
- [x] T036 [US4] Register config router in backend/src/main.py
- [x] T037 [US4] Add rate limiting or auth consideration for production (comment/TODO)
  - Note: Added docstring note about authentication for production

**Checkpoint**: At this point, users can view current config via API - Config API feature complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T038 [P] Create frontend/.env.example with NEXT_PUBLIC_* variables
- [ ] T039 [P] Create frontend/src/lib/config.ts for frontend config utilities
- [ ] T040 Update README.md with configuration instructions
- [ ] T041 Run quickstart.md manual testing checklist
- [x] T042 Run backend tests (uv run pytest) - 107 passed
- [x] T043 Run backend lint (uv run ruff check .) - All checks passed
- [x] T044 Run backend type check (uv run mypy --strict src/) - No issues found

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Core settings functionality
- **User Story 2 (Phase 4)**: Depends on Foundational - Can run parallel to US1
- **User Story 3 (Phase 5)**: Depends on Foundational - Can run parallel to US1/US2
- **User Story 4 (Phase 6)**: Depends on Foundational - Can run parallel to others
- **Polish (Phase 7)**: Depends on all user stories complete

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
│ US1: API Keys     │ │US2: Model   │ │US3: Service     │ │US4: Config  │
│   (P1) 🎯 MVP    │ │ Paths (P1)  │ │  URLs (P2)      │ │  API (P3)   │
└─────────┬─────────┘ └──────┬──────┘ └────────┬────────┘ └──────┬──────┘
          │                  │                 │                 │
          └──────────────────┴────────┬────────┴─────────────────┘
                                      │
                             ┌────────▼────────┐
                             │ Phase 7: Polish │
                             └─────────────────┘
```

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Models before services
3. Services before endpoints
4. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003 can run in parallel (different files)

**Phase 2 (Foundational)**:
- T005, T006, T007, T008 can run in parallel (same file but independent sections)

**User Stories**:
- All test tasks within each story marked [P] can run in parallel
- US1, US2, US3, US4 can be worked on by different team members after Foundational

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Test .env file loading in backend/tests/unit/test_config_loading.py"
Task: "Test environment variable priority in backend/tests/unit/test_config_priority.py"
Task: "Test validation error on invalid values in backend/tests/unit/test_config_validation.py"
Task: "Test SecretStr masking for API keys in backend/tests/unit/test_config_secrets.py"

# After tests fail, implement sequentially:
Task: "Create DeepgramSettings model in backend/src/models/config.py"
Task: "Create OpenAISettings model in backend/src/models/config.py"
Task: "Integrate into root Settings class"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T010)
3. Complete Phase 3: User Story 1 - API Keys (T011-T020)
4. **STOP and VALIDATE**: Test API key management manually
5. Deploy/demo if ready - users can manage API keys via .env

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. **Add User Story 1** → API key management → Deploy/Demo (MVP)
3. **Add User Story 2** → Model path configuration → Deploy/Demo
4. **Add User Story 3** → Service URL configuration → Deploy/Demo
5. **Add User Story 4** → Config inspection API → Deploy/Demo
6. Polish → Final release

### Suggested MVP Scope

**MVP = User Story 1 (API Key Management)**

This delivers the core value proposition:
- Manage sensitive API keys via .env file
- Validation and clear error messages
- SecretStr masking for security

This is the most critical feature for secure configuration management.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Existing backend/src/config.py will be refactored for backward compatibility
