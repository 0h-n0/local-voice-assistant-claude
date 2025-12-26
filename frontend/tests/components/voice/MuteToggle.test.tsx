/**
 * Tests for MuteToggle component.
 * @jest-environment jsdom
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { MuteToggle } from "@/components/voice/MuteToggle";

describe("MuteToggle", () => {
  const onToggle = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("rendering", () => {
    it("should render mute button", () => {
      render(<MuteToggle isMuted={false} onToggle={onToggle} />);

      expect(screen.getByRole("button")).toBeInTheDocument();
    });

    it("should show unmuted icon when not muted", () => {
      render(<MuteToggle isMuted={false} onToggle={onToggle} />);

      expect(screen.getByLabelText(/ミュート/)).toBeInTheDocument();
    });

    it("should show muted icon when muted", () => {
      render(<MuteToggle isMuted={true} onToggle={onToggle} />);

      expect(screen.getByLabelText(/ミュート解除/)).toBeInTheDocument();
    });
  });

  describe("interaction", () => {
    it("should call onToggle when clicked", () => {
      render(<MuteToggle isMuted={false} onToggle={onToggle} />);

      fireEvent.click(screen.getByRole("button"));

      expect(onToggle).toHaveBeenCalled();
    });

    it("should toggle from unmuted to muted", () => {
      render(<MuteToggle isMuted={false} onToggle={onToggle} />);

      fireEvent.click(screen.getByRole("button"));

      expect(onToggle).toHaveBeenCalled();
    });

    it("should toggle from muted to unmuted", () => {
      render(<MuteToggle isMuted={true} onToggle={onToggle} />);

      fireEvent.click(screen.getByRole("button"));

      expect(onToggle).toHaveBeenCalled();
    });
  });

  describe("disabled state", () => {
    it("should not call onToggle when disabled", () => {
      render(<MuteToggle isMuted={false} onToggle={onToggle} disabled />);

      fireEvent.click(screen.getByRole("button"));

      expect(onToggle).not.toHaveBeenCalled();
    });

    it("should show disabled styling when disabled", () => {
      render(<MuteToggle isMuted={false} onToggle={onToggle} disabled />);

      expect(screen.getByRole("button")).toBeDisabled();
    });
  });
});
