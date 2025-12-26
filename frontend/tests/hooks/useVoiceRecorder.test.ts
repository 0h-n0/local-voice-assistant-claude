/**
 * Tests for useVoiceRecorder hook.
 * @jest-environment jsdom
 */

import { renderHook, act } from "@testing-library/react";

// Mock navigator.mediaDevices
const mockGetUserMedia = jest.fn();
const mockMediaRecorder = {
  start: jest.fn(),
  stop: jest.fn(),
  ondataavailable: null as ((event: { data: Blob }) => void) | null,
  onstop: null as (() => void) | null,
  state: "inactive" as RecordingState,
};

// Mock MediaRecorder class
const MockMediaRecorderClass = jest.fn().mockImplementation(() => {
  return mockMediaRecorder;
});
(MockMediaRecorderClass as unknown as { isTypeSupported: jest.Mock }).isTypeSupported = jest.fn().mockReturnValue(true);

// Setup mocks before importing the hook
beforeAll(() => {
  Object.defineProperty(global.navigator, "mediaDevices", {
    value: {
      getUserMedia: mockGetUserMedia,
    },
    writable: true,
  });
  global.MediaRecorder = MockMediaRecorderClass as unknown as typeof MediaRecorder;
});

// Import after mocks are set up
import { useVoiceRecorder } from "@/hooks/useVoiceRecorder";

describe("useVoiceRecorder", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockMediaRecorder.state = "inactive";
  });

  describe("initial state", () => {
    it("should start with isRecording false", () => {
      const { result } = renderHook(() => useVoiceRecorder());
      expect(result.current.state.isRecording).toBe(false);
    });

    it("should start with duration 0", () => {
      const { result } = renderHook(() => useVoiceRecorder());
      expect(result.current.state.duration).toBe(0);
    });

    it("should start with no error", () => {
      const { result } = renderHook(() => useVoiceRecorder());
      expect(result.current.state.error).toBeNull();
    });

    it("should start with unknown permission state", () => {
      const { result } = renderHook(() => useVoiceRecorder());
      expect(result.current.state.hasPermission).toBeNull();
    });
  });

  describe("startRecording", () => {
    it("should request microphone permission", async () => {
      const mockStream = { getTracks: () => [{ stop: jest.fn() }] };
      mockGetUserMedia.mockResolvedValue(mockStream);

      const { result } = renderHook(() => useVoiceRecorder());

      await act(async () => {
        await result.current.startRecording();
      });

      expect(mockGetUserMedia).toHaveBeenCalledWith({ audio: true });
    });

    it("should set isRecording to true on success", async () => {
      const mockStream = { getTracks: () => [{ stop: jest.fn() }] };
      mockGetUserMedia.mockResolvedValue(mockStream);

      const { result } = renderHook(() => useVoiceRecorder());

      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.state.isRecording).toBe(true);
    });

    it("should set error when permission is denied", async () => {
      mockGetUserMedia.mockRejectedValue(
        new DOMException("Permission denied", "NotAllowedError")
      );

      const { result } = renderHook(() => useVoiceRecorder());

      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.state.error).toContain("マイクの使用が許可されていません");
      expect(result.current.state.isRecording).toBe(false);
    });

    it("should set error when no microphone found", async () => {
      mockGetUserMedia.mockRejectedValue(
        new DOMException("No microphone", "NotFoundError")
      );

      const { result } = renderHook(() => useVoiceRecorder());

      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.state.error).toContain("マイクが見つかりません");
      expect(result.current.state.isRecording).toBe(false);
    });
  });

  describe("stopRecording", () => {
    it("should return audio blob when stopping", async () => {
      const mockStream = { getTracks: () => [{ stop: jest.fn() }] };
      mockGetUserMedia.mockResolvedValue(mockStream);

      const { result } = renderHook(() => useVoiceRecorder());

      // Start recording
      await act(async () => {
        await result.current.startRecording();
      });

      // Simulate MediaRecorder behavior
      mockMediaRecorder.state = "recording";

      // Stop recording
      let blob: Blob | null = null;
      await act(async () => {
        const stopPromise = result.current.stopRecording();

        // Simulate data available and stop events
        const testBlob = new Blob(["test audio data"], { type: "audio/webm" });
        mockMediaRecorder.ondataavailable?.({ data: testBlob });
        mockMediaRecorder.onstop?.();

        blob = await stopPromise;
      });

      expect(blob).toBeInstanceOf(Blob);
      expect(result.current.state.isRecording).toBe(false);
    });

    it("should return null if not recording", async () => {
      const { result } = renderHook(() => useVoiceRecorder());

      const blob = await act(async () => {
        return result.current.stopRecording();
      });

      expect(blob).toBeNull();
    });
  });

  describe("cancelRecording", () => {
    it("should stop recording without returning blob", async () => {
      const mockStream = { getTracks: () => [{ stop: jest.fn() }] };
      mockGetUserMedia.mockResolvedValue(mockStream);

      const { result } = renderHook(() => useVoiceRecorder());

      await act(async () => {
        await result.current.startRecording();
      });

      mockMediaRecorder.state = "recording";

      act(() => {
        result.current.cancelRecording();
      });

      expect(result.current.state.isRecording).toBe(false);
    });
  });

  describe("requestPermission", () => {
    it("should return true when permission is granted", async () => {
      const mockStream = { getTracks: () => [{ stop: jest.fn() }] };
      mockGetUserMedia.mockResolvedValue(mockStream);

      const { result } = renderHook(() => useVoiceRecorder());

      let hasPermission: boolean = false;
      await act(async () => {
        hasPermission = await result.current.requestPermission();
      });

      expect(hasPermission).toBe(true);
      expect(result.current.state.hasPermission).toBe(true);
    });

    it("should return false when permission is denied", async () => {
      mockGetUserMedia.mockRejectedValue(
        new DOMException("Permission denied", "NotAllowedError")
      );

      const { result } = renderHook(() => useVoiceRecorder());

      let hasPermission: boolean = true;
      await act(async () => {
        hasPermission = await result.current.requestPermission();
      });

      expect(hasPermission).toBe(false);
      expect(result.current.state.hasPermission).toBe(false);
    });
  });
});
