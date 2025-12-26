"use client";

interface MuteToggleProps {
  /** Whether audio is currently muted */
  isMuted: boolean;
  /** Callback when mute state should be toggled */
  onToggle: () => void;
  /** Whether the toggle is disabled */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Mute toggle button for controlling audio auto-play.
 */
export function MuteToggle({
  isMuted,
  onToggle,
  disabled = false,
  className = "",
}: MuteToggleProps) {
  return (
    <button
      type="button"
      onClick={() => !disabled && onToggle()}
      disabled={disabled}
      className={`flex h-10 w-10 items-center justify-center rounded-lg transition-colors ${
        disabled
          ? "cursor-not-allowed text-zinc-300 dark:text-zinc-600"
          : isMuted
            ? "text-red-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
            : "text-zinc-500 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
      } ${className}`}
      aria-label={isMuted ? "ミュート解除" : "ミュート"}
      title={isMuted ? "ミュート解除" : "ミュート"}
    >
      {isMuted ? (
        <VolumeOffIcon className="h-5 w-5" />
      ) : (
        <VolumeOnIcon className="h-5 w-5" />
      )}
    </button>
  );
}

// =============================================================================
// Icons
// =============================================================================

function VolumeOnIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
      />
    </svg>
  );
}

function VolumeOffIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
      />
    </svg>
  );
}
