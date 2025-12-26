"use client";

import { useCallback, useEffect } from "react";
import { useVoiceRecorder } from "@/hooks/useVoiceRecorder";
import { useAudioContext, audioActions } from "@/components/providers/AudioContext";
import { MicrophoneIcon, StopIcon, LoadingSpinner } from "@/components/shared/Icons";
import { formatDuration } from "@/lib/audio";

interface VoiceButtonProps {
  /** Callback when recording is complete with audio blob */
  onRecordingComplete: (blob: Blob) => void;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Whether to show loading state */
  loading?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Voice recording button component with toggle behavior.
 * Click to start recording, click again to stop and send.
 */
export function VoiceButton({
  onRecordingComplete,
  disabled = false,
  loading = false,
  className = "",
}: VoiceButtonProps) {
  const { state, startRecording, stopRecording, cancelRecording } =
    useVoiceRecorder();
  const { dispatch } = useAudioContext();

  const handleClick = useCallback(async () => {
    if (disabled || loading) return;

    if (state.isRecording) {
      // Stop recording and get blob
      const blob = await stopRecording();
      dispatch(audioActions.stopRecording());

      if (blob) {
        onRecordingComplete(blob);
      }
    } else {
      // Start recording
      dispatch(audioActions.startRecording());
      await startRecording();
    }
  }, [
    disabled,
    loading,
    state.isRecording,
    startRecording,
    stopRecording,
    dispatch,
    onRecordingComplete,
  ]);

  const handleCancel = useCallback(
    (e?: React.MouseEvent) => {
      e?.stopPropagation();
      cancelRecording();
      dispatch(audioActions.stopRecording());
    },
    [cancelRecording, dispatch]
  );

  // Listen for Escape key to cancel recording
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && state.isRecording) {
        handleCancel();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [state.isRecording, handleCancel]);

  // Error state
  if (state.error) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <button
          type="button"
          onClick={handleClick}
          disabled={disabled}
          className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-600 transition-colors hover:bg-red-200 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50"
          aria-label="録音を開始"
          title={state.error}
        >
          <MicrophoneIcon className="h-6 w-6" />
        </button>
        <span className="text-sm text-red-600 dark:text-red-400">
          {state.error}
        </span>
      </div>
    );
  }

  // Recording state
  if (state.isRecording) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        {/* Stop/Send button */}
        <button
          type="button"
          onClick={handleClick}
          className="flex h-12 w-12 items-center justify-center rounded-full bg-red-500 text-white transition-colors hover:bg-red-600"
          aria-label="録音を停止して送信"
        >
          <StopIcon className="h-6 w-6" />
        </button>

        {/* Recording indicator */}
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 animate-pulse rounded-full bg-red-500" />
          <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
            {formatDuration(state.duration)}
          </span>
        </div>

        {/* Cancel button */}
        <button
          type="button"
          onClick={handleCancel}
          className="rounded-lg px-2 py-1 text-sm text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-700 dark:hover:bg-zinc-800 dark:hover:text-zinc-300"
          aria-label="録音をキャンセル"
        >
          キャンセル
        </button>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <button
        type="button"
        disabled
        className={`flex h-12 w-12 items-center justify-center rounded-full bg-zinc-100 text-zinc-400 dark:bg-zinc-800 ${className}`}
        aria-label="処理中"
      >
        <LoadingSpinner className="h-6 w-6" />
      </button>
    );
  }

  // Default state (not recording)
  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled}
      className={`flex h-12 w-12 items-center justify-center rounded-full bg-blue-500 text-white transition-colors hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      aria-label="録音を開始"
    >
      <MicrophoneIcon className="h-6 w-6" />
    </button>
  );
}
