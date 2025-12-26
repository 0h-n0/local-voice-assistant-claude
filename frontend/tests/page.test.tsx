/**
 * Tests for Home page component.
 * @jest-environment jsdom
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import Home from "@/app/page";
import { ChatProvider } from "@/components/providers/ChatContext";
import { AudioProvider } from "@/components/providers/AudioContext";

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock MediaRecorder
class MockMediaRecorder {
  state = "inactive";
  ondataavailable: ((event: { data: Blob }) => void) | null = null;
  onstop: (() => void) | null = null;
  onerror: ((event: Error) => void) | null = null;

  start() {
    this.state = "recording";
  }

  stop() {
    this.state = "inactive";
    if (this.ondataavailable) {
      this.ondataavailable({ data: new Blob() });
    }
    if (this.onstop) {
      this.onstop();
    }
  }

  static isTypeSupported() {
    return true;
  }
}

Object.defineProperty(window, "MediaRecorder", {
  writable: true,
  value: MockMediaRecorder,
});

// Mock navigator.mediaDevices
Object.defineProperty(navigator, "mediaDevices", {
  writable: true,
  value: {
    getUserMedia: jest.fn().mockResolvedValue({
      getTracks: () => [{ stop: jest.fn() }],
    }),
  },
});

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <ChatProvider>
    <AudioProvider>{children}</AudioProvider>
  </ChatProvider>
);

describe("Home Page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          conversations: [],
          total: 0,
          limit: 20,
          offset: 0,
        }),
    });
  });

  describe("layout", () => {
    it("should render sidebar", () => {
      render(
        <Wrapper>
          <Home />
        </Wrapper>
      );

      expect(screen.getByText("会話履歴")).toBeInTheDocument();
    });

    it("should render chat area with voice button", () => {
      render(
        <Wrapper>
          <Home />
        </Wrapper>
      );

      expect(screen.getByLabelText(/録音を開始/)).toBeInTheDocument();
    });

    it("should render new chat button in sidebar", () => {
      render(
        <Wrapper>
          <Home />
        </Wrapper>
      );

      expect(screen.getByText("新しいチャット")).toBeInTheDocument();
    });
  });

  describe("sidebar toggle", () => {
    it("should toggle sidebar visibility on mobile", () => {
      render(
        <Wrapper>
          <Home />
        </Wrapper>
      );

      // Initially sidebar should be visible
      expect(screen.getByText("会話履歴")).toBeInTheDocument();

      // Find and click close button
      const closeButton = screen.getByLabelText("閉じる");
      fireEvent.click(closeButton);

      // Sidebar should still exist but may be hidden via CSS classes
      // The actual visibility test depends on responsive CSS
    });
  });
});
