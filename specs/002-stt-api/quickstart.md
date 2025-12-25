# Quickstart: STT API

**Feature**: 002-stt-api
**Date**: 2025-12-26

## Prerequisites

- Python 3.11+
- NVIDIA GPU with CUDA 11.8+ (recommended) or CPU
- ffmpeg (for audio format conversion)
- Backend server running on `http://localhost:8000`

## Basic Usage

### 1. Audio File Transcription

Upload a WAV file and get transcribed text:

```bash
curl -X POST \
  -F "file=@speech.wav" \
  http://localhost:8000/api/stt/transcribe
```

**Response**:

```json
{
  "text": "こんにちは、今日はいい天気ですね。",
  "duration_seconds": 3.5,
  "processing_time_seconds": 1.2,
  "segments": [
    {
      "text": "こんにちは、",
      "start_time": 0.0,
      "end_time": 1.2
    },
    {
      "text": "今日はいい天気ですね。",
      "start_time": 1.3,
      "end_time": 3.5
    }
  ]
}
```

### 2. Different Audio Formats

The API supports WAV, MP3, FLAC, and OGG formats:

```bash
# MP3 file
curl -X POST -F "file=@speech.mp3" http://localhost:8000/api/stt/transcribe

# FLAC file
curl -X POST -F "file=@speech.flac" http://localhost:8000/api/stt/transcribe
```

### 3. Check Model Status

Verify that the STT model is loaded and ready:

```bash
curl http://localhost:8000/api/stt/status
```

**Response**:

```json
{
  "model_loaded": true,
  "model_name": "reazonspeech-nemo-v2",
  "device": "cuda",
  "memory_usage_mb": 2048.5
}
```

### 4. WebSocket Streaming (Real-time)

Connect via WebSocket for real-time transcription:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/stt/stream');

ws.onopen = () => {
  console.log('Connected');
  // Send audio chunks (16kHz, 16-bit PCM)
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'partial') {
    console.log('Partial:', message.text);
  } else if (message.type === 'final') {
    console.log('Final:', message.text);
  }
};

// Send audio data
ws.send(audioChunk); // ArrayBuffer of PCM data
```

## Error Handling

The API returns structured error responses:

```json
{
  "error_code": "UNSUPPORTED_FORMAT",
  "message": "File format 'pdf' is not supported. Supported formats: wav, mp3, flac, ogg",
  "details": {
    "provided_format": "pdf",
    "supported_formats": ["wav", "mp3", "flac", "ogg"]
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNSUPPORTED_FORMAT | 400 | Unsupported file format |
| FILE_TOO_LARGE | 413 | File exceeds 100MB limit |
| EMPTY_AUDIO | 400 | Empty or invalid audio data |
| MODEL_NOT_LOADED | 503 | Model not yet loaded |
| PROCESSING_ERROR | 500 | Internal processing error |

## Python Client Example

```python
import requests

# File transcription
with open("speech.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/stt/transcribe",
        files={"file": f}
    )
    result = response.json()
    print(result["text"])

# Check status
status = requests.get("http://localhost:8000/api/stt/status").json()
print(f"Model loaded: {status['model_loaded']}")
```

## Performance Notes

- First request may take longer (model initialization)
- GPU provides ~10x faster processing than CPU
- RTF (Real-Time Factor) target: < 0.5 (10s audio in 5s)
- Maximum concurrent requests: 3
