# Feature Specification: STT API - Japanese Speech-to-Text with ReazonSpeech

**Feature Branch**: `002-stt-api`
**Created**: 2025-12-26
**Status**: Draft
**Input**: User description: "reazon-research/reazonspeech-nemo-v2 を用いて音声ファイルまたはマイク入力から日本語テキストを生成する STT API を実装したい。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Audio File Transcription API (Priority: P1)

開発者として、音声ファイルをアップロードしてPOSTリクエストを送信し、日本語テキストに変換された結果を受け取りたい。

**Why this priority**: 音声ファイルからのテキスト変換は最も基本的なSTT機能であり、他のすべての機能の基盤となる。ファイルベースの処理はテストが容易で、まずこれを完成させることでモデルの動作確認ができる。

**Independent Test**: `curl -X POST -F "file=@test.wav" http://localhost:8000/api/stt/transcribe` でテキスト結果が返ること。

**Acceptance Scenarios**:

1. **Given** WAV形式の日本語音声ファイル, **When** /api/stt/transcribe にPOSTリクエスト, **Then** 認識されたテキストとメタデータ（処理時間、信頼度）がJSON形式で返される
2. **Given** MP3形式の音声ファイル, **When** /api/stt/transcribe にPOSTリクエスト, **Then** 内部でWAVに変換され、テキストが返される
3. **Given** 空の音声ファイル, **When** /api/stt/transcribe にPOSTリクエスト, **Then** 適切なエラーメッセージとステータスコード400が返される
4. **Given** サポート外のファイル形式（例：PDF）, **When** /api/stt/transcribe にPOSTリクエスト, **Then** "Unsupported file format" エラーが返される

---

### User Story 2 - Real-time Microphone Streaming (Priority: P2)

開発者として、WebSocket接続を通じてマイク入力をリアルタイムでストリーミングし、逐次的にテキスト変換結果を受け取りたい。

**Why this priority**: リアルタイム音声認識は音声アシスタントの核心機能だが、ファイル処理の基盤が先に必要。ストリーミング処理は複雑なため、P1完了後に取り組む。

**Independent Test**: WebSocketクライアントから音声チャンクを送信し、部分的な認識結果がリアルタイムで返ること。

**Acceptance Scenarios**:

1. **Given** WebSocket接続が確立, **When** 音声チャンク（16kHz, 16-bit PCM）をストリーミング送信, **Then** 部分的な認識結果が逐次返される
2. **Given** ストリーミング中, **When** 発話の区切り（無音区間）を検出, **Then** 確定したテキストセグメントが送信される
3. **Given** WebSocket接続中, **When** クライアントが接続を切断, **Then** リソースが適切に解放される

---

### User Story 3 - Model Health and Status API (Priority: P3)

開発者として、STTモデルのロード状態やリソース使用状況を確認できるAPIを利用したい。

**Why this priority**: 運用監視に必要だが、コア機能の完成後で十分。

**Independent Test**: `/api/stt/status` にGETリクエストでモデル状態が確認できること。

**Acceptance Scenarios**:

1. **Given** モデルがロード済み, **When** /api/stt/status にGETリクエスト, **Then** `{"model_loaded": true, "model_name": "reazonspeech-nemo-v2", ...}` が返される
2. **Given** モデル未ロード, **When** /api/stt/status にGETリクエスト, **Then** `{"model_loaded": false, ...}` が返される

---

### Edge Cases

- 非常に長い音声ファイル（1時間以上）の処理時、タイムアウトせずに処理を完了する
- 無音のみの音声ファイルでは空文字列ではなく適切な応答を返す
- 複数の同時リクエストが来た場合、キューイングして順次処理する
- モデルロード中にリクエストが来た場合、503 Service Unavailable を返す
- 対応していないサンプリングレートの音声は自動的にリサンプリングする

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは `/api/stt/transcribe` エンドポイントで音声ファイル（WAV, MP3, FLAC, OGG）を受け付け、日本語テキストに変換しなければならない
- **FR-002**: システムは reazonspeech-nemo-v2 モデルを使用して音声認識を行わなければならない
- **FR-003**: レスポンスにはテキスト、処理時間（秒）、音声の長さ（秒）を含めなければならない
- **FR-004**: 音声ファイルは16kHzにリサンプリングして処理しなければならない（モデル要件）
- **FR-005**: アップロードされたファイルサイズは最大100MBまで対応しなければならない
- **FR-006**: システムは `/api/stt/stream` WebSocketエンドポイントでリアルタイム音声ストリーミングを受け付けなければならない
- **FR-007**: システムは `/api/stt/status` エンドポイントでモデルの状態を報告しなければならない
- **FR-008**: すべての処理はローカルで完結し、外部APIへの通信を行ってはならない（Constitution: Privacy-First）
- **FR-009**: エラー発生時は構造化されたエラーレスポンス（error_code, message, details）を返さなければならない

### Key Entities

- **TranscriptionRequest**: 音声ファイルのアップロードリクエスト（file: UploadFile, language: Optional[str] = "ja"）
- **TranscriptionResponse**: 認識結果（text: str, duration_seconds: float, processing_time_seconds: float, segments: Optional[List[Segment]]）
- **Segment**: テキストセグメント（text: str, start_time: float, end_time: float）
- **STTStatus**: モデル状態（model_loaded: bool, model_name: str, device: str, memory_usage_mb: float）
- **StreamMessage**: WebSocketメッセージ（type: Literal["partial", "final", "error"], text: str, is_final: bool）

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 10秒の音声ファイルを5秒以内に処理完了できる（RTF < 0.5）
- **SC-002**: モデルロード後のメモリ使用量が4GB以下である
- **SC-003**: 同時10リクエストを処理してもサーバーがクラッシュしない
- **SC-004**: WebSocketストリーミングの遅延が500ms以下である
- **SC-005**: 標準的な日本語音声（NHKニュース程度）で文字誤り率（CER）が10%以下である

## Clarifications

### Session 2025-12-26

- Q: API認証方式は？ → A: 認証なし（ローカル開発専用、CORSで制限）

## Assumptions

- STT APIは認証なしで提供し、CORSによりローカルホスト（localhost:3000）からのアクセスのみ許可する
- CUDA対応のNVIDIA GPUが利用可能である（CPU fallbackもサポートするが、パフォーマンスは低下）
- Python 3.11以上の環境が利用可能
- reazonspeechライブラリとNeMoフレームワークが正常にインストール可能
- 音声ファイルは主に日本語の発話を含む
- 初回モデルロードには数十秒〜数分かかる可能性がある（Hugging Face からのダウンロード含む）
