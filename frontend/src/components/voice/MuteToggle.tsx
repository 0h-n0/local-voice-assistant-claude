"use client";

import { VolumeOnIcon, VolumeOffIcon } from "@/components/shared/Icons";

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
