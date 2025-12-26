/**
 * Tests for useAudioPlayer hook.
 * @jest-environment jsdom
 */

import { renderHook, act } from "@testing-library/react";

// Mock Audio class
const mockAudio = {
  play: jest.fn(),
  pause: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  currentTime: 0,
  src: "",
};

const MockAudioClass = jest.fn().mockImplementation(() => mockAudio);

// Mock URL.createObjectURL and revokeObjectURL
const mockObjectUrl = "blob:http://localhost/test-audio";
const mockCreateObjectURL = jest.fn().mockReturnValue(mockObjectUrl);
const mockRevokeObjectURL = jest.fn();

beforeAll(() => {
  global.Audio = MockAudioClass as unknown as typeof Audio;
  global.URL.createObjectURL = mockCreateObjectURL;
  global.URL.revokeObjectURL = mockRevokeObjectURL;
});

// Import after mocks are set up
import { useAudioPlayer } from "@/hooks/useAudioPlayer";

describe("useAudioPlayer", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockAudio.currentTime = 0;
    mockAudio.play.mockResolvedValue(undefined);
  });

  describe("initial state", () => {
    it("should start with idle state", () => {
      const { result } = renderHook(() => useAudioPlayer());
      expect(result.current.state).toBe("idle");
    });

    it("should start with no error", () => {
      const { result } = renderHook(() => useAudioPlayer());
      expect(result.current.error).toBeNull();
    });
  });

  describe("play", () => {
    it("should create object URL from blob", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });
      const { result } = renderHook(() => useAudioPlayer());

      await act(async () => {
        const playPromise = result.current.play(testBlob);

        // Find and trigger the ended event listener
        const endedHandler = mockAudio.addEventListener.mock.calls.find(
          (call: unknown[]) => call[0] === "ended"
        )?.[1];
        if (endedHandler) {
          endedHandler();
        }

        await playPromise;
      });

      expect(mockCreateObjectURL).toHaveBeenCalledWith(testBlob);
    });

    it("should set state to playing while playing", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });
      const { result } = renderHook(() => useAudioPlayer());

      // Don't await - check state during playback
      act(() => {
        result.current.play(testBlob);
      });

      expect(result.current.state).toBe("playing");
    });

    it("should set state to idle after playback ends", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });
      const { result } = renderHook(() => useAudioPlayer());

      await act(async () => {
        const playPromise = result.current.play(testBlob);

        // Trigger ended event
        const endedHandler = mockAudio.addEventListener.mock.calls.find(
          (call: unknown[]) => call[0] === "ended"
        )?.[1];
        if (endedHandler) {
          endedHandler();
        }

        await playPromise;
      });

      expect(result.current.state).toBe("idle");
    });

    it("should set error on playback failure", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });
      mockAudio.play.mockRejectedValue(new Error("Playback failed"));

      const { result } = renderHook(() => useAudioPlayer());

      await act(async () => {
        try {
          await result.current.play(testBlob);
        } catch {
          // Expected to throw
        }
      });

      expect(result.current.error).toBeTruthy();
      expect(result.current.state).toBe("idle");
    });

    it("should revoke object URL after playback", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });
      const { result } = renderHook(() => useAudioPlayer());

      await act(async () => {
        const playPromise = result.current.play(testBlob);

        const endedHandler = mockAudio.addEventListener.mock.calls.find(
          (call: unknown[]) => call[0] === "ended"
        )?.[1];
        if (endedHandler) {
          endedHandler();
        }

        await playPromise;
      });

      expect(mockRevokeObjectURL).toHaveBeenCalledWith(mockObjectUrl);
    });
  });

  describe("stop", () => {
    it("should pause audio and reset currentTime", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });
      const { result } = renderHook(() => useAudioPlayer());

      act(() => {
        result.current.play(testBlob);
      });

      act(() => {
        result.current.stop();
      });

      expect(mockAudio.pause).toHaveBeenCalled();
      expect(mockAudio.currentTime).toBe(0);
    });

    it("should set state to idle", async () => {
      const testBlob = new Blob(["test audio"], { type: "audio/wav" });
      const { result } = renderHook(() => useAudioPlayer());

      act(() => {
        result.current.play(testBlob);
      });

      act(() => {
        result.current.stop();
      });

      expect(result.current.state).toBe("idle");
    });

    it("should do nothing if not playing", () => {
      const { result } = renderHook(() => useAudioPlayer());

      act(() => {
        result.current.stop();
      });

      expect(mockAudio.pause).not.toHaveBeenCalled();
      expect(result.current.state).toBe("idle");
    });
  });

  describe("playFromText", () => {
    it("should set loading state while fetching", async () => {
      // Mock fetch for TTS
      const mockFetch = jest.fn().mockResolvedValue({
        ok: true,
        blob: () => Promise.resolve(new Blob(["audio"], { type: "audio/wav" })),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useAudioPlayer());

      act(() => {
        result.current.playFromText("こんにちは");
      });

      expect(result.current.state).toBe("loading");
    });
  });
});
