# Quickstart: Voice Chat Web UI

**Feature**: 007-voice-chat-ui
**Date**: 2025-12-27

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ with uv (for backend)
- Modern browser (Chrome, Firefox, Safari 14.1+, Edge)
- Microphone and speakers/headphones

## Setup

### 1. Start Backend

```bash
# From repository root
cd backend

# Install dependencies
uv sync

# Start the server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}
```

### 2. Start Frontend

```bash
# From repository root
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Manual Testing Checklist

### Voice Conversation (User Story 1)

1. **Voice Recording**
   ```
   □ Open http://localhost:3000
   □ Click microphone button
   □ Verify recording indicator appears
   □ Speak a test phrase (e.g., "こんにちは")
   □ Click microphone button again to stop
   □ Verify message appears in chat
   □ Verify audio response plays automatically
   ```

2. **Stop Playback**
   ```
   □ While audio is playing, click stop button
   □ Verify audio stops immediately
   ```

### Conversation History (User Story 2)

1. **View Past Conversations**
   ```
   □ Send multiple messages to create history
   □ Verify messages appear in chat area
   □ Verify sidebar shows conversation
   □ Reload page
   □ Verify conversation persists in sidebar
   □ Click conversation in sidebar
   □ Verify all messages load
   ```

2. **Message Display**
   ```
   □ Verify user messages on right side (blue)
   □ Verify assistant messages on left side (gray)
   □ Verify timestamps are displayed
   ```

### Text Input (User Story 3)

1. **Type Message**
   ```
   □ Type a message in text input
   □ Press Enter or click send button
   □ Verify message appears in chat
   □ Verify assistant responds with audio
   ```

### New Conversation (User Story 4)

1. **Start New Chat**
   ```
   □ Click "New Chat" button
   □ Verify chat area clears
   □ Send a message
   □ Verify new conversation appears in sidebar
   □ Verify old conversation still accessible
   ```

### Audio Controls (User Story 5)

1. **Replay Audio**
   ```
   □ Click replay button on assistant message
   □ Verify audio plays again
   ```

2. **Mute Toggle**
   ```
   □ Toggle mute button
   □ Send new message
   □ Verify audio does NOT auto-play
   □ Verify replay button still works
   □ Toggle mute off
   □ Send new message
   □ Verify audio auto-plays again
   ```

### Error Handling

1. **Microphone Permission Denied**
   ```
   □ Deny microphone permission in browser
   □ Click microphone button
   □ Verify error message appears
   □ Verify text input still works
   ```

2. **Network Error**
   ```
   □ Stop backend server
   □ Try to send message
   □ Verify error message appears
   □ Start backend again
   □ Verify app recovers
   ```

## API Testing (curl)

### List Conversations

```bash
curl -X GET "http://localhost:8000/api/conversations?limit=10" \
  -H "Accept: application/json"
```

### Get Conversation Detail

```bash
# Replace {id} with actual conversation UUID
curl -X GET "http://localhost:8000/api/conversations/{id}" \
  -H "Accept: application/json"
```

### Send Voice Message

```bash
# Record audio first, then:
curl -X POST "http://localhost:8000/api/orchestrator/dialogue" \
  -F "audio=@recording.webm" \
  -F "speed=1.0" \
  --output response.wav
```

### Synthesize Speech (for replay)

```bash
curl -X POST "http://localhost:8000/api/tts/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは", "speed": 1.0}' \
  --output speech.wav
```

### Delete Conversation

```bash
# Replace {id} with actual conversation UUID
curl -X DELETE "http://localhost:8000/api/conversations/{id}"
# Expected: 204 No Content
```

## Development Tips

### Run Frontend Tests

```bash
cd frontend
npm test           # Run all tests
npm test -- --watch  # Watch mode
```

### Run Backend Tests

```bash
cd backend
uv run pytest               # Run all tests
uv run pytest -v            # Verbose
uv run pytest tests/unit/   # Unit tests only
```

### Type Checking

```bash
# Frontend
cd frontend
npm run typecheck

# Backend
cd backend
uv run mypy --strict src/
```

### Linting

```bash
# Frontend
cd frontend
npm run lint

# Backend
cd backend
uv run ruff check .
```

## Common Issues

### Microphone Not Working

1. Check browser permissions: Settings > Privacy > Microphone
2. Ensure HTTPS or localhost (required for getUserMedia)
3. Try different browser

### Audio Not Playing

1. Check browser autoplay policy (may require user interaction)
2. Check volume settings
3. Check browser console for errors

### Backend Connection Failed

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings if on different port
3. Verify `NEXT_PUBLIC_API_URL` environment variable

### TTS Model Not Loaded

1. Ensure TTS model assets are in place
2. Check backend logs for model loading errors
3. Increase `TTS_MAX_CONCURRENT` if needed
