"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import type { VoiceRecorderState, UseVoiceRecorderReturn } from "@/types/audio";
import {
  getBestSupportedMimeType,
  requestMicrophoneAccess,
  stopMediaStream,
} from "@/lib/audio";

/**
 * Hook for recording voice input using MediaRecorder API.
 */
export function useVoiceRecorder(): UseVoiceRecorderReturn {
  const [state, setState] = useState<VoiceRecorderState>({
    isRecording: false,
    duration: 0,
    error: null,
    hasPermission: null,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const resolveStopRef = useRef<((blob: Blob | null) => void) | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
      if (streamRef.current) {
        stopMediaStream(streamRef.current);
      }
    };
  }, []);

  /**
   * Request microphone permission.
   */
  const requestPermission = useCallback(async (): Promise<boolean> => {
    const stream = await requestMicrophoneAccess();

    if (stream) {
      // Permission granted - stop the stream immediately (we just needed to check)
      stopMediaStream(stream);
      setState((prev) => ({ ...prev, hasPermission: true, error: null }));
      return true;
    } else {
      setState((prev) => ({
        ...prev,
        hasPermission: false,
        error: "マイクの使用が許可されていません",
      }));
      return false;
    }
  }, []);

  /**
   * Start recording.
   */
  const startRecording = useCallback(async (): Promise<void> => {
    // Check for browser support
    const mimeType = getBestSupportedMimeType();
    if (!mimeType) {
      setState((prev) => ({
        ...prev,
        error: "お使いのブラウザは音声録音に対応していません",
      }));
      return;
    }

    // Request microphone access
    const stream = await requestMicrophoneAccess();

    if (!stream) {
      // Determine specific error
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
      } catch (error) {
        if (error instanceof DOMException) {
          if (error.name === "NotAllowedError") {
            setState((prev) => ({
              ...prev,
              hasPermission: false,
              error: "マイクの使用が許可されていません。ブラウザの設定を確認してください。",
            }));
          } else if (error.name === "NotFoundError") {
            setState((prev) => ({
              ...prev,
              error: "マイクが見つかりません。マイクが接続されているか確認してください。",
            }));
          } else {
            setState((prev) => ({
              ...prev,
              error: `マイクへのアクセスに失敗しました: ${error.message}`,
            }));
          }
        } else {
          setState((prev) => ({
            ...prev,
            error: "マイクへのアクセスに失敗しました",
          }));
        }
      }
      return;
    }

    streamRef.current = stream;
    chunksRef.current = [];

    // Create MediaRecorder
    try {
      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        chunksRef.current = [];

        if (resolveStopRef.current) {
          resolveStopRef.current(blob);
          resolveStopRef.current = null;
        }
      };

      // Start recording
      mediaRecorder.start(100); // Collect data every 100ms

      // Start duration timer
      const startTime = Date.now();
      durationIntervalRef.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        setState((prev) => ({ ...prev, duration: elapsed }));
      }, 1000);

      setState((prev) => ({
        ...prev,
        isRecording: true,
        duration: 0,
        error: null,
        hasPermission: true,
      }));
    } catch (error) {
      stopMediaStream(stream);
      streamRef.current = null;
      setState((prev) => ({
        ...prev,
        error:
          error instanceof Error
            ? error.message
            : "録音の開始に失敗しました",
      }));
    }
  }, []);

  /**
   * Stop recording and return the audio blob.
   */
  const stopRecording = useCallback(async (): Promise<Blob | null> => {
    if (!mediaRecorderRef.current || !state.isRecording) {
      return null;
    }

    // Clear duration timer
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }

    // Create promise that resolves when onstop fires
    const blobPromise = new Promise<Blob | null>((resolve) => {
      resolveStopRef.current = resolve;
    });

    // Stop recording
    mediaRecorderRef.current.stop();

    // Stop and cleanup stream
    if (streamRef.current) {
      stopMediaStream(streamRef.current);
      streamRef.current = null;
    }

    setState((prev) => ({ ...prev, isRecording: false }));

    return blobPromise;
  }, [state.isRecording]);

  /**
   * Cancel recording without returning blob.
   */
  const cancelRecording = useCallback((): void => {
    // Clear duration timer
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }

    // Stop MediaRecorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      resolveStopRef.current = null; // Don't resolve, we're canceling
      mediaRecorderRef.current.stop();
    }

    // Stop and cleanup stream
    if (streamRef.current) {
      stopMediaStream(streamRef.current);
      streamRef.current = null;
    }

    chunksRef.current = [];

    setState((prev) => ({
      ...prev,
      isRecording: false,
      duration: 0,
    }));
  }, []);

  return {
    state,
    startRecording,
    stopRecording,
    cancelRecording,
    requestPermission,
  };
}
