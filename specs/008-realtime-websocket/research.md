# Research: リアルタイム WebSocket 通信

**Feature**: 008-realtime-websocket
**Date**: 2025-12-27
**Purpose**: Phase 0 research for streaming STT, WebSocket architecture, and LLM streaming

---

## 1. WebSocket Implementation with FastAPI

### Native Support

FastAPI provides native WebSocket support through Starlette. No additional dependencies required.

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")
```

### Connection Management

For single-user local environment, simple in-memory connection tracking is sufficient:

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
```

### Error Handling

```python
from starlette.websockets import WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Response: {data}")
    except WebSocketDisconnect:
        # Handle disconnection gracefully
        pass
```

### Best Practices (2025)

1. **Authentication during handshake**: Verify tokens/cookies before accepting connection
2. **Heartbeat/keepalive**: Send periodic pings to detect stale connections
3. **Message acknowledgement**: For critical messages, implement ACK mechanism
4. **Graceful degradation**: Provide HTTP fallback for WebSocket-incompatible environments

**Sources**:
- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [FastAPI WebSockets: From Basics to Scaling](https://www.pwnchaurasia.dev/posts/tech/websocket_in_fast_api/)
- [Better Stack FastAPI WebSockets Guide](https://betterstack.com/community/guides/scaling-python/fastapi-websockets/)

---

## 2. Streaming STT Options

### Option A: Google Cloud Speech-to-Text (Recommended)

**Pros**:
- Mature streaming API via gRPC
- 125+ language support (including Japanese)
- High accuracy
- Well-documented Python SDK

**Cons**:
- External service (privacy consideration)
- Per-minute billing
- Requires GCP account

**Python SDK**:
```bash
pip install google-cloud-speech
```

**Streaming Code Pattern**:
```python
from google.cloud import speech

def stream_audio():
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ja-JP",
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,  # Get partial results
        single_utterance=True,  # Stop after user stops speaking
    )
    # Stream audio chunks and receive transcripts
```

**Sources**:
- [Google Cloud Speech-to-Text Streaming](https://docs.cloud.google.com/speech-to-text/docs/v1/transcribe-streaming-audio)
- [google-cloud-speech PyPI](https://pypi.org/project/google-cloud-speech/)

### Option B: Azure Speech SDK

**Pros**:
- Comprehensive SDK with streaming support
- 100+ languages (including Japanese)
- On-premises deployment option for privacy
- Real-time diarization support

**Cons**:
- External service (privacy consideration)
- Requires Azure subscription

**Python SDK**:
```bash
pip install azure-cognitiveservices-speech
```

**Key Features**:
- `PushAudioInputStream` for streaming audio
- Automatic format detection with GStreamer
- Real-time interim results

**Sources**:
- [Azure Speech to Text Overview](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-to-text)
- [Real-Time Transcription with Azure](https://medium.com/neural-engineer/azure-ai-speech-to-text-real-time-transcription-58bfd5fd1a28)

### Option C: Deepgram

**Pros**:
- WebSocket-native API (simpler integration)
- Excellent real-time performance
- Nova-3 model with high accuracy for Japanese
- Smart formatting built-in

**Cons**:
- External service (privacy consideration)
- Per-minute billing

**Python SDK**:
```bash
pip install deepgram-sdk
```

**Streaming Pattern**:
```python
from deepgram import DeepgramClient, LiveOptions

client = DeepgramClient(api_key)
options = LiveOptions(
    model="nova-3",
    language="ja",
    smart_format=True,
    interim_results=True,
)

async with client.listen.asyncwebsocket.v("1") as connection:
    connection.on(LiveTranscriptionEvents.Transcript, on_transcript)
    await connection.start(options)
```

**Sources**:
- [Deepgram Python SDK](https://github.com/deepgram/deepgram-python-sdk)
- [Live Transcription with FastAPI](https://deepgram.com/learn/live-transcription-fastapi)

### Recommendation

**Deepgram** is recommended for this project:
1. WebSocket-native API matches our architecture
2. Simpler integration than gRPC-based alternatives
3. Good Japanese language support
4. Built-in interim results for real-time display

---

## 3. LLM Streaming with OpenAI

### Standard Streaming (HTTP SSE)

The existing OpenAI integration already supports streaming via Server-Sent Events:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def stream_response(messages):
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### OpenAI Realtime API (WebSocket Native)

OpenAI provides a Realtime API for native WebSocket streaming:

**Connection**:
```python
import websockets

async with websockets.connect(
    "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview",
    extra_headers={
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1",
    }
) as ws:
    await ws.send(json.dumps({"type": "response.create", ...}))
```

**Note**: The Realtime API is designed for speech-to-speech applications. For text streaming, the standard SSE approach is simpler and sufficient.

### Recommendation

Use **standard HTTP streaming** (SSE) from the existing implementation, then forward chunks through WebSocket to the client:

```python
@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()

    # Receive user message
    user_message = await websocket.receive_json()

    # Stream LLM response
    async for chunk in stream_llm_response(user_message):
        await websocket.send_json({
            "type": "response_chunk",
            "content": chunk,
        })

    await websocket.send_json({"type": "response_complete"})
```

**Sources**:
- [OpenAI Realtime API WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
- [Create Streaming AI Assistant with FastAPI](https://dev.to/dpills/create-a-streaming-ai-assistant-with-chatgpt-fastapi-websockets-and-react-3ehf)

---

## 4. Frontend WebSocket Handling

### Native WebSocket API

Modern browsers support WebSocket natively:

```typescript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case 'transcript_partial':
      setPartialTranscript(data.content);
      break;
    case 'transcript_final':
      setFinalTranscript(data.content);
      break;
    case 'response_chunk':
      appendResponse(data.content);
      break;
  }
};

ws.onclose = () => {
  console.log('Disconnected');
  // Implement reconnection logic
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### React Hook Pattern

```typescript
function useWebSocket(url: string) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => setStatus('connected');
    ws.onclose = () => setStatus('disconnected');
    ws.onmessage = (e) => setMessages(prev => [...prev, JSON.parse(e.data)]);

    setSocket(ws);

    return () => ws.close();
  }, [url]);

  const send = useCallback((data: unknown) => {
    socket?.send(JSON.stringify(data));
  }, [socket]);

  return { socket, status, messages, send };
}
```

### Auto-Reconnection Pattern

```typescript
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 16000]; // Exponential backoff

function useReconnectingWebSocket(url: string) {
  const [reconnectAttempt, setReconnectAttempt] = useState(0);

  const connect = useCallback(() => {
    const ws = new WebSocket(url);

    ws.onclose = () => {
      if (reconnectAttempt < RECONNECT_DELAYS.length) {
        setTimeout(() => {
          setReconnectAttempt(prev => prev + 1);
          connect();
        }, RECONNECT_DELAYS[reconnectAttempt]);
      }
    };

    ws.onopen = () => {
      setReconnectAttempt(0); // Reset on successful connection
    };

    return ws;
  }, [url, reconnectAttempt]);

  // ...
}
```

---

## 5. Message Protocol Design

### Event Types

```typescript
// Server -> Client
type ServerMessage =
  | { type: 'transcript_partial'; content: string; is_final: false }
  | { type: 'transcript_final'; content: string; is_final: true }
  | { type: 'status_update'; status: ProcessingStatus }
  | { type: 'response_chunk'; content: string }
  | { type: 'response_complete'; full_text: string; audio_url?: string }
  | { type: 'error'; code: string; message: string };

// Client -> Server
type ClientMessage =
  | { type: 'audio_chunk'; data: string } // base64 encoded
  | { type: 'audio_end' }
  | { type: 'text_input'; content: string }
  | { type: 'cancel' };

type ProcessingStatus =
  | 'idle'
  | 'recording'
  | 'transcribing'
  | 'generating'
  | 'synthesizing'
  | 'playing';
```

### JSON Message Format

```json
// Server -> Client: Partial transcript
{
  "type": "transcript_partial",
  "content": "今日の天",
  "is_final": false
}

// Server -> Client: Final transcript
{
  "type": "transcript_final",
  "content": "今日の天気は？",
  "is_final": true
}

// Server -> Client: Status update
{
  "type": "status_update",
  "status": "generating"
}

// Server -> Client: Response chunk
{
  "type": "response_chunk",
  "content": "本日の"
}

// Server -> Client: Response complete
{
  "type": "response_complete",
  "full_text": "本日の天気は晴れです。",
  "audio_url": "/api/tts/synthesize?text=..."
}
```

---

## 6. Architecture Decision

### Hybrid Architecture (Recommended)

Combine WebSocket for real-time events with existing HTTP APIs:

```
┌─────────────┐     WebSocket      ┌─────────────────┐
│   Browser   │◄──────────────────►│  FastAPI WS     │
│             │                    │  Endpoint       │
│  - Real-time│                    │                 │
│    display  │                    │  - STT stream   │
│  - Status   │                    │  - LLM stream   │
│    updates  │                    │  - Status push  │
└─────────────┘                    └────────┬────────┘
                                            │
                                   ┌────────▼────────┐
                                   │  Existing HTTP  │
                                   │  APIs           │
                                   │                 │
                                   │  - TTS          │
                                   │  - Conversations│
                                   │  - Orchestrator │
                                   │    (fallback)   │
                                   └─────────────────┘
```

### Benefits

1. **Minimal disruption**: Existing HTTP APIs remain unchanged
2. **Graceful fallback**: HTTP-only mode for WebSocket-incompatible environments
3. **Separation of concerns**: Real-time events via WS, persistent operations via HTTP
4. **Easier testing**: WebSocket and HTTP can be tested independently

---

## 7. Selected Technologies

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Backend WebSocket | FastAPI native | Built-in support, no extra dependencies |
| Streaming STT | Deepgram | WebSocket-native, good Japanese support |
| LLM Streaming | OpenAI SSE → WS forward | Reuse existing implementation |
| Frontend WS | Native WebSocket API | No extra dependencies |
| Reconnection | Custom with exponential backoff | Simple, meets requirements |
| Message Format | JSON | Human-readable, easy debugging |

---

## 8. Open Questions (for Phase 1)

1. **STT Service Selection**: Final decision between Deepgram vs Google vs Azure (consider cost, latency testing)
2. **Audio Chunk Size**: Optimal size for streaming (typically 100-200ms chunks)
3. **Reconnection Strategy**: Maximum retries, backoff ceiling, user notification threshold
4. **Error Recovery**: How to handle mid-stream failures gracefully
