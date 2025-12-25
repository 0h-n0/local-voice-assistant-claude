# Tasks: Project Setup - Backend & Frontend Foundation

**Input**: Design documents from `/specs/001-project-setup/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: TDD is mandated by the Constitution (Principle IV). Test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend tests: `backend/tests/`
- Frontend tests: `frontend/tests/` or `frontend/__tests__/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md in backend/
- [x] T002 Create frontend directory structure per plan.md in frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create pyproject.toml with uv configuration in backend/pyproject.toml
- [x] T004 [P] Create pytest configuration in backend/pyproject.toml (pytest section)
- [x] T005 [P] Create ruff configuration in backend/pyproject.toml (ruff section)
- [x] T006 [P] Create mypy configuration in backend/pyproject.toml (mypy section)
- [x] T007 Run `uv sync` to install dependencies in backend/
- [x] T008 Create conftest.py with pytest fixtures in backend/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Backend Project Initialization (Priority: P1) 🎯 MVP

**Goal**: FastAPIバックエンドプロジェクトを初期化し、ヘルスチェックAPIが動作する状態にする

**Independent Test**: `uv run pytest` でテストが成功、`uv run ruff check .` と `uv run mypy --strict src/` がエラーなく通る

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Contract test for /health endpoint in backend/tests/contract/test_health.py

### Implementation for User Story 1

- [x] T010 [P] [US1] Create HealthResponse Pydantic model in backend/src/models/health.py
- [x] T011 [P] [US1] Create models __init__.py exporting HealthResponse in backend/src/models/__init__.py
- [x] T012 [US1] Implement /health endpoint router in backend/src/api/health.py
- [x] T013 [US1] Create api __init__.py in backend/src/api/__init__.py
- [x] T014 [US1] Create lib __init__.py in backend/src/lib/__init__.py
- [x] T015 [US1] Create main.py with FastAPI app and CORS middleware in backend/src/main.py
- [x] T016 [US1] Create src __init__.py in backend/src/__init__.py
- [x] T017 [US1] Create backend README.md with setup instructions in backend/README.md
- [x] T018 [US1] Verify ruff check passes: `uv run ruff check .` in backend/
- [x] T019 [US1] Verify mypy passes: `uv run mypy --strict src/` in backend/
- [x] T020 [US1] Verify pytest passes: `uv run pytest` in backend/
- [x] T021 [US1] Verify server starts: `uv run uvicorn src.main:app` in backend/

**Checkpoint**: Backend fully functional - can start User Story 2

---

## Phase 4: User Story 2 - Frontend Project Initialization (Priority: P2)

**Goal**: Next.js（TypeScript）フロントエンドプロジェクトを初期化し、開発サーバーが動作する状態にする

**Independent Test**: `npm run dev` でNext.jsが起動、`npm run lint` がエラーなく通る

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T022 [P] [US2] Sample page test in frontend/tests/page.test.tsx (or __tests__/page.test.tsx)

### Implementation for User Story 2

- [x] T023 [US2] Initialize Next.js project with TypeScript + App Router in frontend/ using `npx create-next-app@latest frontend --typescript --app --eslint --tailwind --src-dir --import-alias "@/*"`
- [x] T024 [US2] Add Prettier configuration in frontend/.prettierrc
- [x] T025 [US2] Update ESLint config for stricter rules in frontend/eslint.config.mjs (Next.js 15 flat config)
- [x] T026 [US2] Add Jest + React Testing Library configuration in frontend/jest.config.js
- [x] T027 [P] [US2] Add testing dependencies to package.json in frontend/package.json
- [x] T028 [US2] Create TypeScript types for HealthResponse in frontend/src/types/index.ts
- [x] T029 [US2] Create API client utility in frontend/src/lib/api.ts
- [x] T030 [US2] Create .gitkeep files for empty directories in frontend/src/components/, frontend/src/hooks/
- [x] T031 [US2] Create frontend README.md with setup instructions in frontend/README.md
- [x] T032 [US2] Verify npm run lint passes in frontend/
- [x] T033 [US2] Verify npm run dev starts successfully in frontend/
- [x] T034 [US2] Verify npm test passes (sample test) in frontend/

**Checkpoint**: Frontend fully functional - can start User Story 3

---

## Phase 5: User Story 3 - Development Environment Integration (Priority: P3)

**Goal**: バックエンドとフロントエンドを同時に起動し、統合動作確認ができる状態にする

**Independent Test**: フロントエンドからバックエンドの/healthエンドポイントを呼び出しレスポンスが返る

### Implementation for User Story 3

- [x] T035 [US3] Update frontend page.tsx to call backend /health API in frontend/src/app/page.tsx
- [x] T036 [US3] Verify CORS works: Start backend (port 8000) and frontend (port 3000) and test API call
- [x] T037 [US3] Update root README.md with full stack setup instructions in README.md

**Checkpoint**: Full stack integration complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [x] T038 [P] Validate quickstart.md instructions work end-to-end
- [x] T039 [P] Run all backend quality checks: ruff, mypy, pytest
- [x] T040 [P] Run all frontend quality checks: lint, typecheck, test
- [x] T041 Final code review and cleanup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2)
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - can run in parallel with US1
- **User Story 3 (Phase 5)**: Depends on US1 AND US2 completion
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P3)**: Depends on US1 AND US2 - Integration story

### Within Each User Story

- Tests (T009, T022) MUST be written and FAIL before implementation
- Models before API endpoints
- API endpoints before main.py integration
- Core implementation before verification tasks

### Parallel Opportunities

- T001/T002: Directory setup can run in parallel
- T004/T005/T006: Tool configurations can run in parallel
- T009/T010/T011: Contract test and models can run in parallel (different files)
- US1 and US2 can run in parallel after Phase 2 (if team capacity allows)
- T038/T039/T040: Final validation tasks can run in parallel

---

## Parallel Example: Phase 2

```bash
# Launch tool configurations in parallel:
Task: "Create pytest configuration in backend/pyproject.toml (pytest section)"
Task: "Create ruff configuration in backend/pyproject.toml (ruff section)"
Task: "Create mypy configuration in backend/pyproject.toml (mypy section)"
```

## Parallel Example: User Story 1

```bash
# Launch test and models in parallel (TDD - test written first, then models):
Task: "Contract test for /health endpoint in backend/tests/contract/test_health.py"
Task: "Create HealthResponse Pydantic model in backend/src/models/health.py"
Task: "Create models __init__.py exporting HealthResponse in backend/src/models/__init__.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T008)
3. Complete Phase 3: User Story 1 (T009-T021)
4. **STOP and VALIDATE**: Test backend independently
5. Backend is deployable/demo-able

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Backend) → Test independently → Backend MVP!
3. Add User Story 2 (Frontend) → Test independently → Frontend MVP!
4. Add User Story 3 (Integration) → Test E2E → Full Stack MVP!
5. Polish → Production ready

### Parallel Team Strategy

With 2 developers:

1. Both complete Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Backend)
   - Developer B: User Story 2 (Frontend)
3. Both: User Story 3 (Integration)
4. Both: Polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- TDD is required by Constitution - write tests before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend port: 8000, Frontend port: 3000
