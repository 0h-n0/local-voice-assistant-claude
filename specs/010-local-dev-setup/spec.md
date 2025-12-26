# Feature Specification: ローカル開発環境セットアップ

**Feature Branch**: `010-local-dev-setup`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "ローカルで1コマンドで全サービスが起動するように docker-compose または make コマンドを用意したい"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - ワンコマンドでの開発環境起動 (Priority: P1)

新規開発者やチームメンバーが、プロジェクトをクローン後、1つのコマンドで全サービス（バックエンド、フロントエンド）を起動し、すぐに開発を開始できる。

**Why this priority**: 開発者のオンボーディング時間を大幅に短縮し、環境構築の障壁を取り除くことで開発効率を向上させる。これが最も基本的で重要な機能。

**Independent Test**: `make dev` または同等のコマンドを実行し、ブラウザでフロントエンドにアクセスできることを確認

**Acceptance Scenarios**:

1. **Given** プロジェクトをクローンした状態、**When** 開発者が `make dev` を実行、**Then** バックエンドとフロントエンドが起動し、http://localhost:3000 でUIにアクセスできる
2. **Given** 開発環境が起動している状態、**When** バックエンドAPIを呼び出す、**Then** 正常なレスポンスが返される
3. **Given** 開発環境が起動している状態、**When** ソースコードを変更、**Then** ホットリロードにより変更が反映される

---

### User Story 2 - サービスの停止とクリーンアップ (Priority: P2)

開発者が開発セッションを終了する際、1つのコマンドで全サービスを停止し、必要に応じてリソースをクリーンアップできる。

**Why this priority**: 開発環境の適切な管理は開発フロー全体に関わるが、起動よりは優先度が低い。

**Independent Test**: `make down` を実行し、全プロセスが停止されることを確認

**Acceptance Scenarios**:

1. **Given** 開発環境が起動している状態、**When** 開発者が `make down` を実行、**Then** 全サービスが停止する
2. **Given** 開発環境が停止した状態、**When** ポートの使用状況を確認、**Then** 開発用ポートが解放されている

---

### User Story 3 - 個別サービスの起動 (Priority: P3)

開発者が特定のサービス（バックエンドのみ、フロントエンドのみ）を個別に起動できる。

**Why this priority**: 全体起動に比べて使用頻度は低いが、デバッグや特定機能の開発時に有用。

**Independent Test**: `make backend` を実行し、バックエンドのみ起動することを確認

**Acceptance Scenarios**:

1. **Given** サービスが停止している状態、**When** 開発者が `make backend` を実行、**Then** バックエンドのみが起動する
2. **Given** サービスが停止している状態、**When** 開発者が `make frontend` を実行、**Then** フロントエンドのみが起動する

---

### Edge Cases

- 必要な依存関係（Python、Node.js）がインストールされていない場合、明確なエラーメッセージを表示
- ポートが既に使用されている場合、競合を検出しユーザーに通知
- 環境変数（.env）が設定されていない場合、サンプル設定で起動可能、または明確な指示を表示

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは単一コマンド（`make dev`）で全開発サービスを起動できなければならない
- **FR-002**: システムは単一コマンド（`make down`）で全サービスを停止できなければならない
- **FR-003**: システムは個別サービスの起動コマンド（`make backend`、`make frontend`）を提供しなければならない
- **FR-004**: 起動時に依存関係の確認を行い、不足している場合は明確なエラーメッセージを表示しなければならない
- **FR-005**: バックエンドはホットリロード機能を有効にして起動しなければならない
- **FR-006**: フロントエンドはホットリロード機能を有効にして起動しなければならない
- **FR-007**: 環境変数が未設定の場合、`.env.example` を参照する指示を表示しなければならない
- **FR-008**: ヘルプコマンド（`make help`）で利用可能なコマンド一覧を表示しなければならない

### Key Entities

- **Makefile**: 開発コマンドを定義する中央設定ファイル
- **環境変数**: `.env` ファイルで管理されるサービス設定

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 新規開発者がプロジェクトクローンから最初のページ表示まで5分以内で完了できる
- **SC-002**: `make dev` 実行から全サービス起動完了まで30秒以内
- **SC-003**: ソースコード変更からホットリロード反映まで3秒以内
- **SC-004**: コマンド名と機能が直感的で、ドキュメント参照なしで基本操作が可能

## Assumptions

- 開発者のマシンにPython 3.11+とNode.js 18+がインストール済み
- Makeコマンドが利用可能（macOS/Linux標準、Windows は WSL またはGNU Make for Windows）
- uvとnpmがインストール済み
- Docker Composeは本フェーズでは使用せず、ネイティブ実行を採用（将来的にDocker対応を追加可能）
