"use client";

import { useEffect, useCallback, useRef } from "react";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";
import { useAudioContext, audioActions } from "@/components/providers/AudioContext";

interface AudioPlayerProps {
  /** Audio blob to play */
  audioBlob?: Blob | null;
  /** Whether to auto-play when audioBlob changes */
  autoPlay?: boolean;
  /** Whether audio is muted (prevents auto-play) */
  muted?: boolean;
  /** Message ID for tracking which message is playing */
  messageId?: number;
  /** Whether to show playback controls */
  showControls?: boolean;
  /** Callback when playback ends */
  onPlaybackEnd?: () => void;
  /** Callback when an error occurs */
  onError?: (error: string) => void;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Audio player component for playing voice responses.
 * Supports auto-play and manual control.
 */
export function AudioPlayer({
  audioBlob,
  autoPlay = true,
  muted = false,
  messageId,
  showControls = false,
  onPlaybackEnd,
  onError,
  className = "",
}: AudioPlayerProps) {
  const { state, play, stop, error } = useAudioPlayer();
  const { dispatch } = useAudioContext();

  // Track previous blob to detect changes
  const prevBlobRef = useRef<Blob | null>(null);

  // Handle auto-play when audioBlob changes
  useEffect(() => {
    if (
      audioBlob &&
      audioBlob !== prevBlobRef.current &&
      autoPlay &&
      !muted
    ) {
      prevBlobRef.current = audioBlob;

      if (messageId !== undefined) {
        dispatch(audioActions.startPlayback(messageId));
      }

      play(audioBlob)
        .then(() => {
          dispatch(audioActions.stopPlayback());
          onPlaybackEnd?.();
        })
        .catch((err) => {
          dispatch(audioActions.setPlaybackError(err.message));
          onError?.(err.message);
        });
    }
  }, [audioBlob, autoPlay, muted, messageId, play, dispatch, onPlaybackEnd, onError]);

  // Handle error state
  useEffect(() => {
    if (error) {
      onError?.(error);
    }
  }, [error, onError]);

  // Handle stop
  const handleStop = useCallback(() => {
    stop();
    dispatch(audioActions.stopPlayback());
  }, [stop, dispatch]);

  // If not showing controls, render nothing visible
  if (!showControls) {
    return null;
  }

  // Loading state
  if (state === "loading") {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <LoadingSpinner className="h-5 w-5 text-zinc-400" />
        <span className="text-sm text-zinc-500">読み込み中...</span>
      </div>
    );
  }

  // Playing state
  if (state === "playing") {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <button
          type="button"
          onClick={handleStop}
          data-testid="stop-button"
          className="flex h-8 w-8 items-center justify-center rounded-full bg-red-500 text-white transition-colors hover:bg-red-600"
          aria-label="再生を停止"
        >
          <StopIcon className="h-4 w-4" />
        </button>
        <span className="text-sm text-zinc-500">再生中...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <span className="text-sm text-red-500">{error}</span>
      </div>
    );
  }

  // Idle state (no controls needed)
  return null;
}

// =============================================================================
// Icons
// =============================================================================

function StopIcon({ className = "" }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <rect x="6" y="6" width="12" height="12" rx="2" />
    </svg>
  );
}

function LoadingSpinner({ className = "" }: { className?: string }) {
  return (
    <svg className={`animate-spin ${className}`} fill="none" viewBox="0 0 24 24">
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}
