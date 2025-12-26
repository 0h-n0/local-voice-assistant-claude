"use client";

import {
  createContext,
  useContext,
  useReducer,
  type ReactNode,
  type Dispatch,
} from "react";
import {
  type AudioState,
  type AudioAction,
  initialAudioState,
} from "@/types/audio";

// =============================================================================
// Audio Reducer
// =============================================================================

function audioReducer(state: AudioState, action: AudioAction): AudioState {
  switch (action.type) {
    case "START_RECORDING":
      return {
        ...state,
        isRecording: true,
        recordingError: null,
      };

    case "STOP_RECORDING":
      return {
        ...state,
        isRecording: false,
      };

    case "SET_RECORDING_ERROR":
      return {
        ...state,
        isRecording: false,
        recordingError: action.payload,
      };

    case "START_PLAYBACK":
      return {
        ...state,
        playbackState: "playing",
        currentPlayingMessageId: action.payload,
        playbackError: null,
      };

    case "STOP_PLAYBACK":
      return {
        ...state,
        playbackState: "idle",
        currentPlayingMessageId: null,
      };

    case "SET_PLAYBACK_STATE":
      return {
        ...state,
        playbackState: action.payload,
        // Clear current playing message if going to idle
        currentPlayingMessageId:
          action.payload === "idle" ? null : state.currentPlayingMessageId,
      };

    case "SET_PLAYBACK_ERROR":
      return {
        ...state,
        playbackState: "idle",
        currentPlayingMessageId: null,
        playbackError: action.payload,
      };

    case "TOGGLE_MUTE":
      return {
        ...state,
        isMuted: !state.isMuted,
      };

    case "SET_MUTED":
      return {
        ...state,
        isMuted: action.payload,
      };

    default:
      return state;
  }
}

// =============================================================================
// Context Definition
// =============================================================================

interface AudioContextValue {
  state: AudioState;
  dispatch: Dispatch<AudioAction>;
}

const AudioContext = createContext<AudioContextValue | null>(null);

// =============================================================================
// Provider Component
// =============================================================================

interface AudioProviderProps {
  children: ReactNode;
}

export function AudioProvider({ children }: AudioProviderProps) {
  const [state, dispatch] = useReducer(audioReducer, initialAudioState);

  return (
    <AudioContext.Provider value={{ state, dispatch }}>
      {children}
    </AudioContext.Provider>
  );
}

// =============================================================================
// Hook
// =============================================================================

export function useAudioContext(): AudioContextValue {
  const context = useContext(AudioContext);

  if (!context) {
    throw new Error("useAudioContext must be used within an AudioProvider");
  }

  return context;
}

// =============================================================================
// Action Creators (convenience functions)
// =============================================================================

export const audioActions = {
  startRecording: (): AudioAction => ({
    type: "START_RECORDING",
  }),

  stopRecording: (): AudioAction => ({
    type: "STOP_RECORDING",
  }),

  setRecordingError: (error: string | null): AudioAction => ({
    type: "SET_RECORDING_ERROR",
    payload: error,
  }),

  startPlayback: (messageId: number): AudioAction => ({
    type: "START_PLAYBACK",
    payload: messageId,
  }),

  stopPlayback: (): AudioAction => ({
    type: "STOP_PLAYBACK",
  }),

  setPlaybackState: (state: AudioState["playbackState"]): AudioAction => ({
    type: "SET_PLAYBACK_STATE",
    payload: state,
  }),

  setPlaybackError: (error: string | null): AudioAction => ({
    type: "SET_PLAYBACK_ERROR",
    payload: error,
  }),

  toggleMute: (): AudioAction => ({
    type: "TOGGLE_MUTE",
  }),

  setMuted: (isMuted: boolean): AudioAction => ({
    type: "SET_MUTED",
    payload: isMuted,
  }),
};
