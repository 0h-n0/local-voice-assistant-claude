# Quickstart: リアルタイム WebSocket 通信

**Feature**: 008-realtime-websocket
**Date**: 2025-12-27

## Prerequisites

- Node.js 18+
- Python 3.11+
- `uv` (Python package manager)
- Deepgram API key (for streaming STT)
- OpenAI API key (for LLM)
- Existing backend and frontend from Feature 007

## Setup

### 1. Install Backend Dependencies

```bash
cd backend
uv add websockets  # Already included via FastAPI
```

### 2. Configure Streaming STT

Create or update `.env` in the backend directory:

```bash
# Deepgram STT (for streaming)
DEEPGRAM_API_KEY=your_deepgram_api_key

# OpenAI (existing)
OPENAI_API_KEY=your_openai_api_key

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL=30  # seconds
WS_MAX_AUDIO_DURATION=60  # seconds
```

### 3. Start Development Servers

**Backend:**
```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Quick Verification

### Test WebSocket Connection

Using `websocat` (install with `cargo install websocat` or `brew install websocat`):

```bash
# Connect to WebSocket endpoint
websocat ws://localhost:8000/ws/realtime

# You should receive:
# {"type":"connection_ack","session_id":"...","server_time":"..."}
```

### Test Ping/Pong

Send in websocat:
```json
{"type":"pong","timestamp":"2025-12-27T00:00:00Z"}
```

### Test Text Input

Send in websocat:
```json
{"type":"text_input","content":"こんにちは"}
```

Expected response sequence:
```json
{"type":"status_update","status":"generating",...}
{"type":"response_chunk","content":"こんにちは",...}
{"type":"response_chunk","content":"！",...}
{"type":"response_complete","full_text":"こんにちは！お手伝いできることはありますか？",...}
{"type":"status_update","status":"idle",...}
```

## Manual Testing Checklist

### Connection & Reconnection

- [ ] Page load establishes WebSocket connection
- [ ] Connection indicator shows "Connected" (green)
- [ ] Disconnect network → indicator shows "Reconnecting" (yellow)
- [ ] Reconnect network → automatic reconnection occurs
- [ ] After 5 failed attempts → indicator shows "Disconnected" (red)

### Real-time Transcription

- [ ] Click microphone button → status shows "Recording"
- [ ] Speak → partial transcript appears in real-time
- [ ] Stop speaking → final transcript appears
- [ ] Transcript updates smoothly without flickering

### Processing Status

- [ ] After voice input → status shows "Transcribing"
- [ ] After transcription → status shows "Generating"
- [ ] Response text streams character by character
- [ ] After response → status shows "Synthesizing" (if TTS enabled)
- [ ] After audio ready → status returns to "Idle"

### Error Handling

- [ ] Long audio (>60s) → error message appears
- [ ] Empty audio → error message appears
- [ ] Network error during processing → error with retry option
- [ ] STT service error → graceful fallback message

### HTTP Fallback

- [ ] Block WebSocket in browser DevTools
- [ ] Voice input still works via HTTP API
- [ ] Status indicators still update (but not real-time)

## Troubleshooting

### WebSocket Connection Fails

1. Check backend is running on port 8000
2. Check browser console for WebSocket errors
3. Verify no firewall blocking WebSocket connections

```bash
# Test WebSocket endpoint directly
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: $(openssl rand -base64 16)" \
  http://localhost:8000/ws/realtime
```

### STT Streaming Not Working

1. Check Deepgram API key is set
2. Check Deepgram service status
3. Test with direct API call:

```bash
curl -X POST "https://api.deepgram.com/v1/listen" \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: audio/wav" \
  --data-binary @test.wav
```

### Audio Not Recording

1. Check browser microphone permissions
2. Check browser console for MediaRecorder errors
3. Test microphone in browser settings

### Response Streaming Not Working

1. Check OpenAI API key
2. Verify LLM service is responding:

```bash
curl -X POST "http://localhost:8000/api/llm/generate" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

## Development Tips

### Enable Debug Logging

**Backend:**
```bash
# In .env
LOG_LEVEL=DEBUG
```

**Frontend:**
```typescript
// In useWebSocket hook
useEffect(() => {
  if (process.env.NODE_ENV === 'development') {
    console.log('[WS]', status, message);
  }
}, [status, message]);
```

### Mock WebSocket for Testing

```typescript
// In tests
class MockWebSocket {
  onopen: () => void = () => {};
  onmessage: (event: MessageEvent) => void = () => {};
  onclose: () => void = () => {};
  onerror: (error: Event) => void = () => {};

  send(data: string) {
    console.log('Mock send:', data);
  }

  close() {
    this.onclose();
  }

  // Simulate server message
  simulateMessage(data: object) {
    this.onmessage({ data: JSON.stringify(data) } as MessageEvent);
  }
}
```

## Next Steps

After quickstart verification, proceed with:

1. Run `/speckit.tasks` to generate task list
2. Implement tests first (TDD)
3. Implement backend WebSocket endpoint
4. Implement frontend hooks and components
5. Integration testing
6. Performance tuning
