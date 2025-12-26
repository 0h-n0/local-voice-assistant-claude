# Quickstart: TTS API (Text-to-Speech)

**Date**: 2025-12-26
**Feature**: [spec.md](./spec.md) | [plan.md](./plan.md)

## Prerequisites

1. Python 3.11+ with uv
2. TTS モデルファイル（後述）

## Setup

### 1. Install Dependencies

```bash
cd backend
uv add style-bert-vits2 scipy
```

### 2. Download TTS Model

モデルファイルを `model_assets/` に配置：

```bash
mkdir -p model_assets/jvnv-F1-jp

# Hugging Face Hub からダウンロード（例）
# または手動でファイルを配置
```

必要なファイル：
- `config.json`
- `jvnv-F1-jp_e160_s14000.safetensors`
- `style_vectors.npy`

### 3. Start Server

```bash
cd backend
uv run uvicorn src.main:app --reload
```

## API Usage

### Synthesize Speech

```bash
# 基本的な音声合成
curl -X POST "http://localhost:8000/api/tts/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは"}' \
  --output hello.wav

# 話速を変更（1.5倍速）
curl -X POST "http://localhost:8000/api/tts/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "早口で話します", "speed": 1.5}' \
  --output fast.wav
```

### Check Service Status

```bash
curl "http://localhost:8000/api/tts/status"
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "jvnv-F1-jp",
  "device": "cpu",
  "last_check": "2025-12-26T10:30:00Z"
}
```

## Python Client Example

```python
import httpx
from pathlib import Path

async def synthesize_speech(text: str, speed: float = 1.0) -> bytes:
    """テキストを音声に変換"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/tts/synthesize",
            json={"text": text, "speed": speed},
        )
        response.raise_for_status()
        return response.content

# Usage
audio_data = await synthesize_speech("こんにちは")
Path("output.wav").write_bytes(audio_data)
```

## Configuration

環境変数で設定可能（オプション）：

| Variable | Description | Default |
|----------|-------------|---------|
| `TTS_MODEL_PATH` | モデルファイルのパス | `model_assets/jvnv-F1-jp` |
| `TTS_DEVICE` | 推論デバイス | `cpu` |
| `TTS_MAX_CONCURRENT` | 最大同時リクエスト数 | `3` |

## Testing

```bash
cd backend

# ユニットテスト
uv run pytest tests/unit/test_tts_service.py -v

# 統合テスト（モデル必要）
uv run pytest tests/integration/test_tts_api.py -v
```

## Troubleshooting

### Model Not Loaded

```
{"error_code": "MODEL_NOT_LOADED", "message": "TTS model is not loaded"}
```

**Solution**: モデルファイルが正しいパスに配置されているか確認。

### Service Busy

```
{"error_code": "SERVICE_BUSY", "message": "Service is processing too many requests"}
```

**Solution**: 同時リクエスト数の上限に達している。しばらく待ってリトライ。

### CUDA Out of Memory

GPU 使用時にメモリ不足が発生した場合：

```bash
# CPU に切り替え
export TTS_DEVICE=cpu
```
