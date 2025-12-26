# Quickstart: Voice Dialogue Orchestrator

**Feature**: 005-voice-orchestrator
**Date**: 2025-12-26

## Prerequisites

1. バックエンドサーバーが起動していること
2. STT/LLM/TTSの各モデルがロード済みであること
3. `OPENAI_API_KEY` 環境変数が設定されていること

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orchestrator/dialogue` | 音声対話実行 |
| GET | `/api/orchestrator/status` | ステータス確認 |

---

## Usage Examples

### 1. 音声対話の実行

#### curl

```bash
# 基本的な使用法
curl -X POST http://localhost:8000/api/orchestrator/dialogue \
  -F "audio=@question.wav" \
  -o response.wav

# 話速を指定（1.5倍速）
curl -X POST http://localhost:8000/api/orchestrator/dialogue \
  -F "audio=@question.wav" \
  -F "speed=1.5" \
  -o response.wav

# ヘッダー情報も表示
curl -X POST http://localhost:8000/api/orchestrator/dialogue \
  -F "audio=@question.wav" \
  -o response.wav \
  -D - 2>/dev/null | head -20
```

#### Python (httpx)

```python
import httpx

async def voice_dialogue(audio_path: str, speed: float = 1.0) -> bytes:
    """Execute voice dialogue and return audio response."""
    async with httpx.AsyncClient() as client:
        with open(audio_path, "rb") as f:
            response = await client.post(
                "http://localhost:8000/api/orchestrator/dialogue",
                files={"audio": ("audio.wav", f, "audio/wav")},
                data={"speed": str(speed)},
                timeout=60.0,
            )

        response.raise_for_status()

        # メタデータをヘッダーから取得
        print(f"Total time: {response.headers.get('X-Processing-Time-Total')}s")
        print(f"STT time: {response.headers.get('X-Processing-Time-STT')}s")
        print(f"LLM time: {response.headers.get('X-Processing-Time-LLM')}s")
        print(f"TTS time: {response.headers.get('X-Processing-Time-TTS')}s")
        print(f"Input text: {response.headers.get('X-Input-Text-Length')} chars")
        print(f"Output text: {response.headers.get('X-Output-Text-Length')} chars")

        return response.content

# 使用例
import asyncio

audio_data = asyncio.run(voice_dialogue("question.wav"))
with open("response.wav", "wb") as f:
    f.write(audio_data)
```

#### JavaScript (fetch)

```javascript
async function voiceDialogue(audioBlob, speed = 1.0) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'audio.wav');
  formData.append('speed', speed.toString());

  const response = await fetch('http://localhost:8000/api/orchestrator/dialogue', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`${error.error_code}: ${error.message}`);
  }

  // メタデータを取得
  console.log('Total time:', response.headers.get('X-Processing-Time-Total'));
  console.log('Input text:', response.headers.get('X-Input-Text-Length'), 'chars');
  console.log('Output text:', response.headers.get('X-Output-Text-Length'), 'chars');

  return await response.blob();
}

// 使用例（ブラウザ録音との組み合わせ）
const audioBlob = await recordAudio(); // 別途実装
const responseBlob = await voiceDialogue(audioBlob);
const audioUrl = URL.createObjectURL(responseBlob);
new Audio(audioUrl).play();
```

---

### 2. ステータス確認

#### curl

```bash
curl http://localhost:8000/api/orchestrator/status | jq
```

#### レスポンス例

```json
{
  "status": "healthy",
  "services": {
    "stt": {
      "status": "healthy",
      "details": {
        "model_loaded": true,
        "model_name": "reazonspeech-nemo-v2",
        "device": "cuda"
      }
    },
    "llm": {
      "status": "healthy",
      "details": {
        "api_configured": true,
        "model": "gpt-4o-mini"
      }
    },
    "tts": {
      "status": "healthy",
      "details": {
        "model_loaded": true,
        "model_name": "jvnv-F1-jp",
        "device": "cpu"
      }
    }
  },
  "timestamp": "2025-12-26T10:30:00Z"
}
```

---

## Error Handling

### エラーレスポンス形式

```json
{
  "error_code": "SPEECH_RECOGNITION_FAILED",
  "message": "Could not recognize speech in the audio",
  "details": null,
  "retry_after": null
}
```

### 主なエラーコードと対処

| Error Code | HTTP Status | 対処法 |
|------------|-------------|--------|
| `INVALID_AUDIO_FORMAT` | 400 | サポート形式（WAV, MP3, M4A, WebM）を使用 |
| `AUDIO_TOO_SHORT` | 400 | 0.5秒以上の音声を送信 |
| `AUDIO_TOO_LONG` | 400 | 5分以内の音声を送信 |
| `SPEECH_RECOGNITION_FAILED` | 422 | 明瞭な音声で再試行 |
| `TOO_MANY_REQUESTS` | 429 | `retry_after` 秒後に再試行 |
| `*_SERVICE_UNAVAILABLE` | 503 | サービスの復旧を待つ |

### Python エラーハンドリング例

```python
import httpx

async def voice_dialogue_with_retry(audio_path: str, max_retries: int = 3):
    """Execute voice dialogue with retry logic."""
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            with open(audio_path, "rb") as f:
                response = await client.post(
                    "http://localhost:8000/api/orchestrator/dialogue",
                    files={"audio": f},
                    timeout=60.0,
                )

            if response.status_code == 200:
                return response.content

            error = response.json()
            error_code = error.get("error_code")

            # リトライ可能なエラー
            if error_code in ("TOO_MANY_REQUESTS", "LLM_RATE_LIMITED"):
                retry_after = error.get("retry_after", 5)
                print(f"Rate limited. Retrying in {retry_after}s...")
                await asyncio.sleep(retry_after)
                continue

            # リトライ不可能なエラー
            raise Exception(f"{error_code}: {error.get('message')}")

        raise Exception("Max retries exceeded")
```

---

## Configuration

### 環境変数

| Variable | Default | Description |
|----------|---------|-------------|
| `ORCHESTRATOR_MAX_CONCURRENT` | 5 | 最大同時リクエスト数 |
| `ORCHESTRATOR_TIMEOUT` | 30 | 処理タイムアウト（秒） |
| `ORCHESTRATOR_MAX_AUDIO_DURATION` | 300 | 最大音声長（秒） |
| `ORCHESTRATOR_MIN_AUDIO_DURATION` | 0.5 | 最小音声長（秒） |

---

## Testing

### 手動テスト

```bash
# 1. サーバー起動
cd backend
uv run uvicorn src.main:app --reload

# 2. ステータス確認
curl http://localhost:8000/api/orchestrator/status | jq .status
# 期待値: "healthy"

# 3. 音声対話テスト
curl -X POST http://localhost:8000/api/orchestrator/dialogue \
  -F "audio=@test_audio.wav" \
  -o response.wav && \
  echo "Success: response.wav created"

# 4. 応答音声を再生
ffplay -autoexit response.wav
```

### 自動テスト

```bash
cd backend

# 全テスト実行
uv run pytest tests/ -v

# オーケストレーターテストのみ
uv run pytest tests/ -v -k orchestrator
```
