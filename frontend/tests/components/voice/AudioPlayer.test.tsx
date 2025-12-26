/**
 * Tests for AudioPlayer component.
 * @jest-environment jsdom
 */

import React from "react";
import { render } from "@testing-library/react";
import { AudioPlayer } from "@/components/voice/AudioPlayer";
import { AudioProvider } from "@/components/providers/AudioContext";

// Mock useAudioPlayer hook
const mockPlay = jest.fn().mockResolvedValue(undefined);
const mockStop = jest.fn();
const mockPlayFromText = jest.fn().mockResolvedValue(undefined);

jest.mock("@/hooks/useAudioPlayer", () => ({
  useAudioPlayer: () => ({
    state: "idle",
    play: mockPlay,
    playFromText: mockPlayFromText,
    stop: mockStop,
    error: null,
  }),
}));

// Wrapper with providers
const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <AudioProvider>{children}</AudioProvider>
);

describe("AudioPlayer", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("auto-play behavior", () => {
    it("should auto-play when audioBlob is provided and autoPlay is true", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });

      render(
        <Wrapper>
          <AudioPlayer audioBlob={testBlob} autoPlay />
        </Wrapper>
      );

      // Wait a tick for the useEffect to run
      await new Promise((resolve) => setTimeout(resolve, 0));
      expect(mockPlay).toHaveBeenCalledWith(testBlob);
    });

    it("should not auto-play when autoPlay is false", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });

      render(
        <Wrapper>
          <AudioPlayer audioBlob={testBlob} autoPlay={false} />
        </Wrapper>
      );

      await new Promise((resolve) => setTimeout(resolve, 0));
      expect(mockPlay).not.toHaveBeenCalled();
    });

    it("should not auto-play when muted", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });

      render(
        <Wrapper>
          <AudioPlayer audioBlob={testBlob} autoPlay muted />
        </Wrapper>
      );

      await new Promise((resolve) => setTimeout(resolve, 0));
      expect(mockPlay).not.toHaveBeenCalled();
    });
  });

  describe("controls visibility", () => {
    it("should not render visible content when showControls is false", () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });

      const { container } = render(
        <Wrapper>
          <AudioPlayer audioBlob={testBlob} showControls={false} />
        </Wrapper>
      );

      // Component should return null when not showing controls
      expect(container.firstChild).toBeNull();
    });
  });

  describe("no audio blob", () => {
    it("should not play when audioBlob is null", async () => {
      render(
        <Wrapper>
          <AudioPlayer audioBlob={null} autoPlay />
        </Wrapper>
      );

      await new Promise((resolve) => setTimeout(resolve, 0));
      expect(mockPlay).not.toHaveBeenCalled();
    });
  });
});
