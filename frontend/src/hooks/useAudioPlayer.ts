"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import type { PlaybackState, UseAudioPlayerReturn } from "@/types/audio";
import { createAudioUrl, revokeAudioUrl } from "@/lib/audio";
import { synthesizeSpeech } from "@/lib/api";

/**
 * Hook for playing audio using HTML5 Audio API.
 */
export function useAudioPlayer(): UseAudioPlayerReturn {
  const [state, setState] = useState<PlaybackState>("idle");
  const [error, setError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const currentUrlRef = useRef<string | null>(null);

  /**
   * Cleanup current audio and URL.
   */
  const cleanup = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      // Event listeners are removed in the play function after they fire
      audioRef.current = null;
    }

    if (currentUrlRef.current) {
      revokeAudioUrl(currentUrlRef.current);
      currentUrlRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  /**
   * Play audio from a Blob.
   */
  const play = useCallback(
    async (audioBlob: Blob): Promise<void> => {
      // Cleanup any existing playback
      cleanup();
      setError(null);

      try {
        // Create object URL and audio element
        const url = createAudioUrl(audioBlob);
        currentUrlRef.current = url;

        const audio = new Audio(url);
        audioRef.current = audio;

        // Create promise that resolves on end or rejects on error
        const playPromise = new Promise<void>((resolve, reject) => {
          const handleEnded = () => {
            audio.removeEventListener("ended", handleEnded);
            audio.removeEventListener("error", handleError);
            setState("idle");
            cleanup();
            resolve();
          };

          const handleError = () => {
            audio.removeEventListener("ended", handleEnded);
            audio.removeEventListener("error", handleError);
            setError("音声の再生に失敗しました");
            setState("idle");
            cleanup();
            reject(new Error("音声の再生に失敗しました"));
          };

          audio.addEventListener("ended", handleEnded);
          audio.addEventListener("error", handleError);
        });

        // Start playback
        setState("playing");
        await audio.play();

        // Wait for playback to complete
        await playPromise;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "音声の再生に失敗しました";
        setError(errorMessage);
        setState("idle");
        cleanup();
        throw err;
      }
    },
    [cleanup]
  );

  /**
   * Play audio from text by requesting TTS.
   */
  const playFromText = useCallback(
    async (text: string, speed = 1.0): Promise<void> => {
      cleanup();
      setError(null);
      setState("loading");

      try {
        // Request TTS synthesis
        const { audio: audioBlob } = await synthesizeSpeech(text, speed);

        // Play the synthesized audio
        await play(audioBlob);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "音声の合成に失敗しました";
        setError(errorMessage);
        setState("idle");
        throw err;
      }
    },
    [cleanup, play]
  );

  /**
   * Stop playback.
   */
  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setState("idle");
    cleanup();
  }, [cleanup]);

  return {
    state,
    play,
    playFromText,
    stop,
    error,
  };
}
