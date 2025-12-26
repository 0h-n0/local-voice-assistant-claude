/**
 * Audio utility functions for voice recording and playback.
 */

// =============================================================================
// Audio Format Detection
// =============================================================================

/**
 * Supported audio MIME types in order of preference.
 */
const SUPPORTED_MIME_TYPES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/ogg;codecs=opus",
  "audio/ogg",
  "audio/mp4",
] as const;

/**
 * Gets the best supported MIME type for recording.
 * @returns The best supported MIME type or null if none supported.
 */
export function getBestSupportedMimeType(): string | null {
  if (typeof MediaRecorder === "undefined") {
    return null;
  }

  for (const mimeType of SUPPORTED_MIME_TYPES) {
    if (MediaRecorder.isTypeSupported(mimeType)) {
      return mimeType;
    }
  }

  return null;
}

// =============================================================================
// Permission Handling
// =============================================================================

/**
 * Checks if microphone permission is granted.
 * @returns Promise resolving to permission state.
 */
export async function checkMicrophonePermission(): Promise<PermissionState> {
  try {
    const result = await navigator.permissions.query({
      name: "microphone" as PermissionName,
    });
    return result.state;
  } catch {
    // permissions.query not supported (e.g., Firefox)
    // Return "prompt" to indicate unknown state
    return "prompt";
  }
}

/**
 * Requests microphone access.
 * @returns Promise resolving to MediaStream if granted, null if denied.
 */
export async function requestMicrophoneAccess(): Promise<MediaStream | null> {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    return stream;
  } catch (error) {
    if (error instanceof DOMException) {
      if (error.name === "NotAllowedError") {
        console.warn("Microphone permission denied");
      } else if (error.name === "NotFoundError") {
        console.warn("No microphone found");
      }
    }
    return null;
  }
}

/**
 * Stops all tracks in a MediaStream.
 * @param stream - The MediaStream to stop.
 */
export function stopMediaStream(stream: MediaStream): void {
  stream.getTracks().forEach((track) => track.stop());
}

// =============================================================================
// Audio Blob Handling
// =============================================================================

/**
 * Creates an object URL for an audio blob.
 * Remember to revoke with URL.revokeObjectURL when done.
 * @param blob - The audio blob.
 * @returns The object URL.
 */
export function createAudioUrl(blob: Blob): string {
  return URL.createObjectURL(blob);
}

/**
 * Revokes an object URL to free memory.
 * @param url - The object URL to revoke.
 */
export function revokeAudioUrl(url: string): void {
  URL.revokeObjectURL(url);
}

// =============================================================================
// Audio Playback
// =============================================================================

/**
 * Creates an Audio element from a blob.
 * @param blob - The audio blob.
 * @returns The Audio element.
 */
export function createAudioElement(blob: Blob): HTMLAudioElement {
  const url = createAudioUrl(blob);
  const audio = new Audio(url);
  return audio;
}

/**
 * Plays an audio element with proper error handling.
 * @param audio - The Audio element to play.
 * @returns Promise that resolves when playback ends.
 */
export async function playAudio(audio: HTMLAudioElement): Promise<void> {
  return new Promise((resolve, reject) => {
    const handleEnded = () => {
      cleanup();
      resolve();
    };

    const handleError = () => {
      cleanup();
      reject(new Error("Audio playback failed"));
    };

    const cleanup = () => {
      audio.removeEventListener("ended", handleEnded);
      audio.removeEventListener("error", handleError);
    };

    audio.addEventListener("ended", handleEnded);
    audio.addEventListener("error", handleError);

    audio.play().catch((error) => {
      cleanup();
      reject(error);
    });
  });
}

/**
 * Stops audio playback and resets position.
 * @param audio - The Audio element to stop.
 */
export function stopAudio(audio: HTMLAudioElement): void {
  audio.pause();
  audio.currentTime = 0;
}

// =============================================================================
// Duration Formatting
// =============================================================================

/**
 * Formats seconds as MM:SS.
 * @param seconds - Duration in seconds.
 * @returns Formatted string.
 */
export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

// =============================================================================
// Browser Support Detection
// =============================================================================

/**
 * Checks if the browser supports the required audio APIs.
 * @returns Object with support status for each API.
 */
export function checkBrowserAudioSupport(): {
  mediaRecorder: boolean;
  getUserMedia: boolean;
  audioContext: boolean;
  htmlAudio: boolean;
} {
  return {
    mediaRecorder: typeof MediaRecorder !== "undefined",
    getUserMedia:
      typeof navigator !== "undefined" &&
      typeof navigator.mediaDevices !== "undefined" &&
      typeof navigator.mediaDevices.getUserMedia === "function",
    audioContext:
      typeof AudioContext !== "undefined" ||
      typeof (window as unknown as { webkitAudioContext?: unknown })
        .webkitAudioContext !== "undefined",
    htmlAudio: typeof Audio !== "undefined",
  };
}

/**
 * Checks if the browser fully supports voice features.
 * @returns true if all required APIs are available.
 */
export function isVoiceSupported(): boolean {
  const support = checkBrowserAudioSupport();
  return (
    support.mediaRecorder &&
    support.getUserMedia &&
    support.htmlAudio
  );
}
