# Feature Specification: Voice Chat Web UI

**Feature Branch**: `007-voice-chat-ui`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "ChatGPTのように会話履歴が表示され、音声入力と音声出力ができるWeb UIを実装したい。"

## Overview

A web-based chat interface similar to ChatGPT that displays conversation history and enables voice-based interaction. Users can speak their messages (voice input) and hear responses read aloud (voice output), while also having the option to type and read text traditionally.

## Clarifications

### Session 2025-12-27

- Q: What is the voice recording trigger mode? → A: Click to start recording, click again to stop and send (toggle mode)
- Q: How should audio be handled for replay? → A: Re-request audio from TTS backend on each replay (no caching)

## User Scenarios & Testing

### User Story 1 - Voice Conversation (Priority: P1)

As a user, I want to have a voice conversation with the assistant so that I can interact hands-free without typing.

**Why this priority**: Voice interaction is the core differentiator of this feature. Without voice input and output, this would be a standard text chat interface. This enables hands-free usage which is the primary value proposition.

**Independent Test**: Can be fully tested by clicking a microphone button, speaking a question, and hearing the assistant's response played back through speakers. Delivers immediate value for hands-free interaction.

**Acceptance Scenarios**:

1. **Given** I am on the chat interface, **When** I click the microphone button and speak "今日の天気は？", **Then** my spoken words appear as a text message in the conversation history
2. **Given** I have sent a voice message, **When** the assistant responds, **Then** the response is automatically played aloud through my speakers
3. **Given** voice playback is in progress, **When** I click a stop button, **Then** the audio playback stops immediately
4. **Given** I am recording my voice, **When** I click the stop recording button, **Then** the recording stops and my message is sent

---

### User Story 2 - Conversation History Display (Priority: P1)

As a user, I want to see my conversation history displayed in a ChatGPT-like interface so that I can follow the flow of the conversation and reference previous messages.

**Why this priority**: Visual conversation history is essential for users to track context and review previous exchanges. This is equally critical as voice interaction for a complete chat experience.

**Independent Test**: Can be fully tested by sending multiple messages and verifying they appear in chronological order with clear visual distinction between user and assistant messages.

**Acceptance Scenarios**:

1. **Given** I am on the chat interface, **When** the page loads, **Then** I see previous conversations in the sidebar (if any exist)
2. **Given** I have an ongoing conversation, **When** I send a message, **Then** my message appears on the right side of the chat area
3. **Given** the assistant responds, **When** the response is received, **Then** it appears on the left side of the chat area with a distinct visual style
4. **Given** I have multiple past conversations, **When** I click on a conversation in the sidebar, **Then** the full message history for that conversation is displayed

---

### User Story 3 - Text Input Alternative (Priority: P2)

As a user, I want to type messages in addition to voice input so that I can use the chat in environments where speaking is not appropriate.

**Why this priority**: While voice is the primary input, text input provides essential flexibility for quiet environments, privacy concerns, or accessibility needs.

**Independent Test**: Can be fully tested by typing a message in a text input field and pressing send, then verifying the message appears in the conversation history.

**Acceptance Scenarios**:

1. **Given** I am on the chat interface, **When** I type a message in the text input and press Enter, **Then** my message is sent and appears in the conversation history
2. **Given** I am typing a message, **When** I click the send button, **Then** my message is sent and the input field is cleared
3. **Given** I have typed a message, **When** I start voice recording, **Then** the typed text is preserved and can be sent after recording

---

### User Story 4 - New Conversation (Priority: P2)

As a user, I want to start a new conversation so that I can begin a fresh topic without previous context.

**Why this priority**: Managing multiple conversations is important for organization but not essential for basic functionality.

**Independent Test**: Can be fully tested by clicking a "New Chat" button and verifying a fresh conversation starts without previous messages.

**Acceptance Scenarios**:

1. **Given** I am in an existing conversation, **When** I click the "New Chat" button, **Then** a new empty conversation is created and displayed
2. **Given** I start a new conversation, **When** I send my first message, **Then** the conversation is saved and appears in the sidebar

---

### User Story 5 - Audio Playback Control (Priority: P3)

As a user, I want to control audio playback of assistant responses so that I can replay messages or mute when needed.

**Why this priority**: Enhanced audio controls improve user experience but are not essential for basic voice interaction.

**Independent Test**: Can be fully tested by receiving a response, clicking replay to hear it again, and toggling mute to silence future responses.

**Acceptance Scenarios**:

1. **Given** an assistant response has been played, **When** I click the replay button on that message, **Then** the response audio plays again
2. **Given** automatic audio playback is enabled, **When** I toggle the mute option, **Then** future responses are not automatically played aloud
3. **Given** audio is muted, **When** I toggle mute off, **Then** automatic audio playback resumes for new responses

---

### Edge Cases

- What happens when the microphone is not available or permission is denied?
  - System displays a clear error message and falls back to text-only input mode
- What happens when voice recognition fails to understand speech?
  - System displays an error message asking the user to try again or use text input
- What happens when audio output fails (no speakers or audio blocked)?
  - System displays the text response and shows a warning about audio unavailability
- What happens during slow network conditions?
  - Loading indicators are shown during processing, and partial responses are streamed as they become available
- What happens when the user speaks in a different language than expected?
  - System processes the input as-is; language detection is handled by the backend services
- What happens when a very long conversation exceeds screen space?
  - Conversation history is scrollable with automatic scroll to the latest message

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a microphone button that toggles recording state (click to start, click again to stop and send)
- **FR-002**: System MUST convert spoken audio to text and display it as a user message
- **FR-003**: System MUST play assistant responses aloud automatically (when not muted)
- **FR-004**: System MUST display conversation messages in a scrollable chat area with clear user/assistant distinction
- **FR-005**: System MUST provide a text input field as an alternative to voice input
- **FR-006**: System MUST display a list of past conversations in a sidebar
- **FR-007**: System MUST allow users to select and view past conversations
- **FR-008**: System MUST provide a "New Chat" button to start fresh conversations
- **FR-009**: System MUST provide visual recording indicator while voice input is active
- **FR-010**: System MUST provide controls to stop recording or cancel voice input
- **FR-011**: System MUST provide a stop button to halt audio playback
- **FR-012**: System MUST provide a replay button for each assistant response (re-requests audio from TTS backend, no caching)
- **FR-013**: System MUST provide a mute toggle for automatic audio playback
- **FR-014**: System MUST request microphone permission before first voice input
- **FR-015**: System MUST handle microphone/audio errors gracefully with user-friendly messages
- **FR-016**: System MUST show loading indicators during voice processing and response generation
- **FR-017**: System MUST automatically scroll to show the latest message

### Key Entities

- **Conversation**: A collection of messages between the user and assistant, identified by a unique ID, with creation and last update timestamps
- **Message**: A single exchange unit containing the sender role (user or assistant), text content, creation timestamp, and optional audio reference
- **Audio Playback State**: Current state of audio output (playing, paused, stopped, muted)

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can complete a voice-to-voice conversation cycle (speak, receive spoken response) in under 10 seconds for typical queries
- **SC-002**: Voice input accuracy matches the underlying speech recognition service with no additional errors introduced by the UI
- **SC-003**: Conversation history loads within 2 seconds when selecting a past conversation
- **SC-004**: Users can successfully switch between voice and text input without page reload
- **SC-005**: Audio playback controls (stop, replay, mute) respond within 100ms of user action
- **SC-006**: The interface is usable on both desktop and mobile browsers
- **SC-007**: 95% of first-time users can complete their first voice interaction without reading documentation

## Assumptions

- The backend already provides STT (Speech-to-Text), LLM, and TTS (Text-to-Speech) services via the orchestrator API
- The backend already provides conversation storage API endpoints (from Feature 006)
- Modern browsers with Web Audio API and MediaRecorder API support are the target platform
- Users have a working microphone and speakers/headphones
- Japanese language is the primary language for voice interaction
- The interface will be primarily used on devices with stable internet connection

## Out of Scope

- Real-time voice streaming (push-to-talk model is used instead)
- Voice wake word detection (explicit button press required)
- Multi-user or collaborative chat
- Message editing or deletion
- Conversation export functionality
- Custom voice selection for TTS output
- Offline mode support
