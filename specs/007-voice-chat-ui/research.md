# Research: Voice Chat Web UI

**Feature**: 007-voice-chat-ui
**Date**: 2025-12-27

## Research Topics

### 1. Browser Audio Recording API

**Decision**: Use MediaRecorder API with WebM/Opus format

**Rationale**:
- MediaRecorder is the standard browser API for audio capture
- Widely supported in modern browsers (Chrome, Firefox, Safari 14.1+, Edge)
- WebM/Opus provides good compression while maintaining quality
- Backend orchestrator already handles audio format conversion via pydub

**Alternatives Considered**:
- Web Audio API with ScriptProcessorNode: Deprecated, more complex
- getUserMedia + manual encoding: Unnecessary complexity
- Third-party libraries (RecordRTC): Adds dependency, MediaRecorder sufficient

**Implementation Notes**:
```typescript
// Request microphone access
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

// Create recorder with preferred format
const mediaRecorder = new MediaRecorder(stream, {
  mimeType: 'audio/webm;codecs=opus'
});

// Collect audio chunks
const chunks: Blob[] = [];
mediaRecorder.ondataavailable = (e) => chunks.push(e.data);

// On stop, create blob for upload
mediaRecorder.onstop = () => {
  const blob = new Blob(chunks, { type: 'audio/webm' });
  // Send to backend
};
```

### 2. Audio Playback Strategy

**Decision**: Use HTML5 Audio element with Web Audio API fallback

**Rationale**:
- HTML5 Audio element is simplest for basic playback
- Sufficient for play/stop/replay functionality
- No need for advanced audio processing
- Works with WAV format returned by TTS endpoint

**Alternatives Considered**:
- Web Audio API AudioBufferSourceNode: More control but overkill for simple playback
- Howler.js: External dependency, unnecessary for requirements
- MediaSource Extensions: Designed for streaming, not needed here

**Implementation Notes**:
```typescript
// Create audio element from blob
const audioUrl = URL.createObjectURL(wavBlob);
const audio = new Audio(audioUrl);

// Play with promise handling
await audio.play();

// Stop playback
audio.pause();
audio.currentTime = 0;

// Cleanup
URL.revokeObjectURL(audioUrl);
```

### 3. State Management Approach

**Decision**: React Context + useReducer for global state, local state for component-specific UI

**Rationale**:
- Avoids external dependencies (Redux, Zustand)
- Sufficient for single-page chat application
- Context provides conversation and audio state globally
- Local state handles recording UI, input field, etc.

**Alternatives Considered**:
- Redux: Overkill for this scope, adds boilerplate
- Zustand: Good option but adds dependency
- Jotai/Recoil: Atomic state unnecessary here
- React Query/TanStack Query: Good for server state, but adds dependency

**State Structure**:
```typescript
interface ChatState {
  conversations: ConversationSummary[];
  currentConversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

interface AudioState {
  isRecording: boolean;
  isPlaying: boolean;
  isMuted: boolean;
  currentPlayingMessageId: string | null;
}
```

### 4. Styling Approach

**Decision**: Tailwind CSS with component-based styling

**Rationale**:
- Already referenced in constitution (Technical Stack TBD)
- Utility-first approach allows rapid UI development
- Good for responsive design (desktop + mobile)
- No external CSS framework dependencies beyond Tailwind

**Alternatives Considered**:
- CSS Modules: More isolation but slower iteration
- Styled-components: Runtime CSS-in-JS, performance overhead
- Plain CSS: Maintenance burden, harder to maintain consistency
- shadcn/ui: Could use for components, but adds complexity

**Component Styling Pattern**:
```tsx
// Message bubble example
<div className={cn(
  "max-w-[80%] rounded-lg p-3",
  isUser
    ? "bg-blue-500 text-white ml-auto"
    : "bg-gray-100 text-gray-900"
)}>
  {content}
</div>
```

### 5. API Integration Pattern

**Decision**: Fetch API with typed wrapper functions

**Rationale**:
- Fetch is built-in, no dependency needed
- Existing api.ts pattern in codebase
- Type-safe wrappers provide good DX
- Handles FormData for multipart uploads (voice)

**Alternatives Considered**:
- Axios: External dependency, fetch sufficient
- ky: Fetch wrapper, unnecessary abstraction
- React Query: Good for caching, but adds dependency and we don't cache audio

**API Client Extensions**:
```typescript
// Voice dialogue
async function sendVoiceMessage(audioBlob: Blob, speed?: number): Promise<{
  audio: Blob;
  metadata: ProcessingMetadata;
}>;

// Conversations
async function getConversations(limit?: number, offset?: number): Promise<ConversationListResponse>;
async function getConversation(id: string): Promise<ConversationDetail>;
async function deleteConversation(id: string): Promise<void>;

// TTS for replay
async function synthesizeSpeech(text: string, speed?: number): Promise<Blob>;
```

### 6. Error Handling Strategy

**Decision**: Error boundaries for components, try-catch for async operations, user-friendly messages

**Rationale**:
- Error boundaries prevent full app crash
- Async errors caught and displayed in UI
- Backend error codes mapped to user messages
- Graceful degradation (voice fails → text mode)

**Error Mapping**:
```typescript
const ERROR_MESSAGES: Record<string, string> = {
  INVALID_AUDIO_FORMAT: "音声形式が無効です。もう一度お試しください。",
  SPEECH_RECOGNITION_FAILED: "音声を認識できませんでした。もう一度話してください。",
  STT_SERVICE_UNAVAILABLE: "音声認識サービスが利用できません。",
  // ... etc
};
```

### 7. Responsive Design Approach

**Decision**: Mobile-first with sidebar collapse on small screens

**Rationale**:
- SC-006 requires desktop and mobile browser support
- Sidebar takes full screen on mobile, slides out
- Chat area adapts to available width
- Voice button prominent on both sizes

**Breakpoints**:
- Mobile: < 768px (sidebar hidden, toggle button)
- Desktop: ≥ 768px (sidebar visible, 280px width)

## Dependencies Summary

### Required (npm install)

| Package | Version | Purpose |
|---------|---------|---------|
| (none)  |         | All using built-in browser APIs and existing Next.js setup |

### Peer Dependencies (already present)

| Package | Notes |
|---------|-------|
| next | Already in package.json |
| react | Already in package.json |
| tailwindcss | Already configured |
| typescript | Already configured |

## Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| Audio recording format | WebM/Opus via MediaRecorder, backend converts |
| Audio playback method | HTML5 Audio element |
| State management | React Context + useReducer |
| Styling framework | Tailwind CSS (already configured) |
| External API dependencies | None - use fetch API |
| Error handling | Error boundaries + async try-catch |

## Next Steps

1. Generate data-model.md with frontend TypeScript types
2. Generate API contracts (OpenAPI already exists in backend, create frontend types)
3. Generate quickstart.md for development workflow
