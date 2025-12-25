# Feature Specification: Project Setup - Backend & Frontend Foundation

**Feature Branch**: `001-project-setup`
**Created**: 2025-12-25
**Status**: Draft
**Input**: User description: "ローカル音声アシスタントのバックエンドとフロントエンドの基本プロジェクト構成を作成したい。FastAPI + React (or Next.js) 構成。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Backend Project Initialization (Priority: P1)

開発者として、FastAPIバックエンドプロジェクトを初期化し、必要な開発ツール（uv, ruff, mypy, pytest）が正しく設定された状態で開発を開始できるようにしたい。

**Why this priority**: バックエンドはAPIを提供する基盤であり、フロントエンドより先に構築する必要がある。また、憲法で定められたツールチェーン（uv, pydantic, ruff）の設定が最優先。

**Independent Test**: `uv run pytest` でテストが実行でき、`uv run ruff check .` と `uv run mypy --strict .` がエラーなく通ること。

**Acceptance Scenarios**:

1. **Given** 空のbackendディレクトリ, **When** プロジェクト初期化コマンドを実行, **Then** pyproject.tomlが作成され、uvで依存関係がインストールできる
2. **Given** 初期化済みのbackendプロジェクト, **When** `uv run ruff check .`を実行, **Then** エラーなく完了する
3. **Given** 初期化済みのbackendプロジェクト, **When** `uv run pytest`を実行, **Then** サンプルテストが成功する
4. **Given** 初期化済みのbackendプロジェクト, **When** `uv run python -m src.main`を実行, **Then** FastAPIサーバーが起動しヘルスチェックエンドポイントが応答する

---

### User Story 2 - Frontend Project Initialization (Priority: P2)

開発者として、Next.js（TypeScript）フロントエンドプロジェクトを初期化し、必要な開発ツール（ESLint, Prettier, Jest）が正しく設定された状態で開発を開始できるようにしたい。

**Why this priority**: フロントエンドはバックエンドAPIに依存するため、バックエンドの後に構築。ただし、並行開発も可能なため早期に準備が必要。

**Independent Test**: `npm run dev` でNext.jsが起動し、`npm run lint` と `npm run typecheck` がエラーなく通ること。

**Acceptance Scenarios**:

1. **Given** 空のfrontendディレクトリ, **When** `npx create-next-app`を実行, **Then** Next.jsプロジェクトがTypeScript + App Router構成で作成される
2. **Given** 初期化済みのfrontendプロジェクト, **When** `npm run lint`を実行, **Then** ESLintがエラーなく完了する
3. **Given** 初期化済みのfrontendプロジェクト, **When** `npm run dev`を実行, **Then** 開発サーバーが起動しブラウザでアクセスできる
4. **Given** 初期化済みのfrontendプロジェクト, **When** `npm test`を実行, **Then** Jestテストランナーが起動しサンプルテストが成功する

---

### User Story 3 - Development Environment Integration (Priority: P3)

開発者として、バックエンドとフロントエンドを同時に起動し、統合開発環境として動作確認できるようにしたい。

**Why this priority**: 個別のプロジェクトが動作した後の統合確認。基本構成が完了してから実施。

**Independent Test**: 両プロジェクトを起動し、フロントエンドからバックエンドのヘルスチェックAPIを呼び出せること。

**Acceptance Scenarios**:

1. **Given** 両プロジェクトが初期化済み, **When** バックエンドとフロントエンドを同時に起動, **Then** それぞれのポートで正常に動作する
2. **Given** 両サーバーが起動中, **When** フロントエンドからバックエンドAPIを呼び出す, **Then** CORSエラーなくレスポンスを受信できる

---

### Edge Cases

- バックエンドの依存関係インストールが失敗した場合、明確なエラーメッセージを表示
- Node.jsまたはPythonのバージョンが要件を満たさない場合、起動時に警告を表示
- ポートが既に使用中の場合、代替ポートを使用するか明確なエラーを表示

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: バックエンドプロジェクトはuvでパッケージ管理できる構成でなければならない
- **FR-002**: バックエンドはFastAPIフレームワークを使用し、非同期処理をサポートしなければならない
- **FR-003**: バックエンドはPydantic v2でリクエスト/レスポンスモデルを定義しなければならない
- **FR-004**: バックエンドはruffでリント・フォーマット、mypyで型チェックできなければならない
- **FR-005**: バックエンドはpytestでテスト実行できなければならない
- **FR-006**: フロントエンドはNext.js (App Router) + TypeScript構成でなければならない
- **FR-007**: フロントエンドはESLint + Prettierでコード品質を管理できなければならない
- **FR-008**: フロントエンドはJest + React Testing Libraryでテスト実行できなければならない
- **FR-009**: バックエンドは `/health` エンドポイントを提供し、サービス状態を返さなければならない
- **FR-010**: 開発環境ではCORSを許可し、フロントエンドからのAPI呼び出しを可能にしなければならない

### Key Entities

- **Backend Application**: FastAPIアプリケーションインスタンス、ルーター、ミドルウェア設定
- **Frontend Application**: Next.jsアプリケーション、ページ構成、API呼び出しユーティリティ
- **Health Status**: バックエンドの状態を表すレスポンスモデル（status, version, timestamp）

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 開発者がREADMEの手順に従い、5分以内にバックエンド開発環境を起動できる
- **SC-002**: 開発者がREADMEの手順に従い、5分以内にフロントエンド開発環境を起動できる
- **SC-003**: すべてのリンター・型チェッカーがエラーなく通過する（バックエンド: ruff, mypy / フロントエンド: ESLint, tsc）
- **SC-004**: 初期テストスイートが100%成功する
- **SC-005**: フロントエンドからバックエンドAPIへのリクエストが1秒以内に完了する

## Assumptions

- Python 3.11以上がシステムにインストールされている
- Node.js 18以上がシステムにインストールされている
- uvがシステムにインストールされている、またはインストール手順がREADMEに記載される
- 開発は単一マシン上で行われ、バックエンドはlocalhost:8000、フロントエンドはlocalhost:3000で起動する
