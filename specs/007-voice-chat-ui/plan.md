# Implementation Plan: Voice Chat Web UI

**Branch**: `007-voice-chat-ui` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-voice-chat-ui/spec.md`

## Summary

Implement a ChatGPT-like web interface for voice-based conversation. The frontend will use Next.js with React to provide:
- Voice input via browser MediaRecorder API (toggle recording mode)
- Voice output via Web Audio API (auto-play, replay from TTS backend)
- Conversation history display with sidebar navigation
- Integration with existing backend APIs (orchestrator, conversations, TTS)

## Technical Context

**Language/Version**: TypeScript 5.x (Frontend), Python 3.11+ (Backend - existing)
**Primary Dependencies**: Next.js 16+, React 19+, Tailwind CSS (styling)
**Storage**: SQLite via existing conversation storage API (Feature 006)
**Testing**: Jest + React Testing Library (Frontend), pytest (Backend - existing)
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge) with Web Audio API and MediaRecorder API
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Voice-to-response cycle < 10 seconds, UI interactions < 100ms
**Constraints**: No audio caching (re-request TTS on replay), browser microphone permission required
**Scale/Scope**: Single-user local assistant, conversation history stored in SQLite

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ✅ PASS | All audio processed locally via existing backend; no external data transmission |
| II. Performance-Conscious | ✅ PASS | SC-001 targets < 10s cycle; UI interactions < 100ms (SC-005) |
| III. Simplicity-First | ✅ PASS | Uses existing APIs, minimal new dependencies, no audio caching complexity |
| IV. TDD | ✅ PASS | Tests written first for all components (Jest + RTL) |
| V. Modular Architecture | ✅ PASS | Separate components: chat area, sidebar, voice controls, message display |
| VI. Observability | ✅ PASS | Processing time headers from backend; console logging in dev mode |
| VII. Language-Idiomatic | ✅ PASS | TypeScript strict mode, React hooks, Tailwind CSS |

## Project Structure

### Documentation (this feature)

```text
specs/007-voice-chat-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (frontend types)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/              # Existing: orchestrator, conversations, tts
│   ├── models/           # Existing: Pydantic models
│   ├── services/         # Existing: business logic
│   └── db/               # Existing: SQLite conversation storage
└── tests/                # Existing: pytest tests

frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── layout.tsx    # Root layout with providers
│   │   └── page.tsx      # Main chat page
│   ├── components/       # React components
│   │   ├── chat/         # Chat-related components
│   │   │   ├── ChatArea.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── InputArea.tsx
│   │   ├── sidebar/      # Sidebar components
│   │   │   ├── Sidebar.tsx
│   │   │   └── ConversationList.tsx
│   │   └── voice/        # Voice control components
│   │       ├── VoiceButton.tsx
│   │       ├── AudioPlayer.tsx
│   │       └── MuteToggle.tsx
│   ├── hooks/            # Custom React hooks
│   │   ├── useVoiceRecorder.ts
│   │   ├── useAudioPlayer.ts
│   │   ├── useConversations.ts
│   │   └── useChat.ts
│   ├── lib/              # Utilities and API client
│   │   ├── api.ts        # Existing + extensions
│   │   └── audio.ts      # Audio utilities
│   └── types/            # TypeScript type definitions
│       ├── index.ts      # Existing + extensions
│       ├── conversation.ts
│       └── audio.ts
└── tests/
    ├── components/       # Component tests
    ├── hooks/            # Hook tests
    └── lib/              # Utility tests
```

**Structure Decision**: Web application with frontend/backend separation. Frontend extends existing Next.js scaffolding. Backend uses existing APIs without modifications.

## Complexity Tracking

No Constitution violations - table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none)    |            |                                     |
