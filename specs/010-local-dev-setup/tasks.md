# Tasks: ローカル開発環境セットアップ

**Input**: Design documents from `/specs/010-local-dev-setup/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: 本機能はMakefileベースの開発ツールのため、自動テストは不要。手動検証で確認。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Makefile**: Repository root `/Makefile`
- **Backend**: `backend/` directory
- **Frontend**: `frontend/` directory

---

## Phase 1: Setup

**Purpose**: プロジェクト初期設定

- [x] T001 Create Makefile at repository root `/Makefile`
- [x] T002 [P] Add `.PHONY` declarations for all targets in `/Makefile`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 全User Storyで共有する基盤機能

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add dependency check function (check-deps) in `/Makefile`
- [x] T004 [P] Add help target with command descriptions in `/Makefile`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - ワンコマンドでの開発環境起動 (Priority: P1) 🎯 MVP

**Goal**: `make dev` で全サービス（バックエンド + フロントエンド）を並列起動

**Independent Test**: `make dev` を実行し、http://localhost:3000 と http://localhost:8000/health にアクセスできることを確認

### Implementation for User Story 1

- [x] T005 [US1] Add backend target to start FastAPI with hot reload in `/Makefile`
- [x] T006 [US1] Add frontend target to start Next.js dev server in `/Makefile`
- [x] T007 [US1] Add dev target with parallel process management (trap + background jobs) in `/Makefile`
- [x] T008 [US1] Add dependency checks before service start (Python, Node.js, uv, npm) in `/Makefile`
- [x] T009 [US1] Add .env check with helpful message if missing in `/Makefile`

**Checkpoint**: `make dev` で全サービスが起動し、Ctrl+C で停止できることを確認

---

## Phase 4: User Story 2 - サービスの停止とクリーンアップ (Priority: P2)

**Goal**: `make down` で全サービスを確実に停止

**Independent Test**: `make down` を実行し、使用中のポートが解放されることを確認

### Implementation for User Story 2

- [x] T010 [US2] Add down target to stop all running processes in `/Makefile`
- [x] T011 [US2] Add port cleanup logic (kill processes on ports 3000, 8000) in `/Makefile`

**Checkpoint**: `make down` で全プロセスが終了し、ポートが解放されることを確認

---

## Phase 5: User Story 3 - 個別サービスの起動 (Priority: P3)

**Goal**: バックエンドのみ、フロントエンドのみを個別に起動可能

**Independent Test**: `make backend` でバックエンドのみ、`make frontend` でフロントエンドのみが起動することを確認

### Implementation for User Story 3

- [x] T012 [US3] Ensure backend target works standalone with dependency check in `/Makefile`
- [x] T013 [US3] Ensure frontend target works standalone with dependency check in `/Makefile`
- [x] T014 [US3] Add install target for dependency installation (uv sync + npm install) in `/Makefile`

**Checkpoint**: 各サービスが独立して起動・停止できることを確認

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: ドキュメント更新と最終検証

- [x] T015 [P] Update README.md with make commands usage
- [x] T016 Run quickstart.md validation (manual walkthrough)
- [x] T017 Verify all make targets with `make help`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Core dev workflow
- **User Story 2 (Phase 4)**: Depends on Foundational - Can run parallel to US1
- **User Story 3 (Phase 5)**: Depends on Foundational - Can run parallel to US1/US2
- **Polish (Phase 6)**: Depends on all user stories complete

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
│ US1: make dev     │ │US2: make    │ │US3: make        │
│   (P1) 🎯 MVP    │ │ down (P2)   │ │ backend/frontend│
└─────────┬─────────┘ └──────┬──────┘ └────────┬────────┘
          │                  │                 │
          └──────────────────┴────────┬────────┘
                                      │
                             ┌────────▼────────┐
                             │ Phase 6: Polish │
                             └─────────────────┘
```

### Within Each User Story

1. Dependency checks before service start
2. Core implementation
3. Error handling and messages
4. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T001, T002 can run in parallel (different aspects of same file, but T001 creates file first)

**Phase 2 (Foundational)**:
- T003, T004 can run in parallel (independent functions)

**User Stories**:
- US1, US2, US3 can be worked on in parallel after Foundational
- Within US1: T005, T006 can run in parallel (different targets)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T004)
3. Complete Phase 3: User Story 1 (T005-T009)
4. **STOP and VALIDATE**: Test `make dev` manually
5. Deploy/demo if ready - developers can start using the tool

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. **Add User Story 1** → `make dev` works → Deploy/Demo (MVP)
3. **Add User Story 2** → `make down` works → Deploy/Demo
4. **Add User Story 3** → Individual service control → Deploy/Demo
5. Polish → Final release with documentation

### Suggested MVP Scope

**MVP = User Story 1 (make dev)**

This delivers the core value proposition:
- Single command to start all services
- Hot reload enabled
- Dependency checks with clear error messages

This is the most critical feature for developer productivity.

---

## Notes

- [P] tasks = different files or independent sections, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Makefile uses tabs for indentation (not spaces)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
