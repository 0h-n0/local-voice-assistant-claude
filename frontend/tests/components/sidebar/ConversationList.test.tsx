/**
 * Tests for ConversationList component.
 * @jest-environment jsdom
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { ConversationList } from "@/components/sidebar/ConversationList";

const mockConversations = [
  {
    id: "conv-1",
    message_count: 3,
    created_at: "2025-12-27T10:00:00Z",
    updated_at: "2025-12-27T11:00:00Z",
  },
  {
    id: "conv-2",
    message_count: 5,
    created_at: "2025-12-26T09:00:00Z",
    updated_at: "2025-12-26T10:00:00Z",
  },
];

describe("ConversationList", () => {
  const onSelect = jest.fn();
  const onDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("rendering", () => {
    it("should render list of conversations", () => {
      render(
        <ConversationList
          conversations={mockConversations}
          onSelect={onSelect}
        />
      );

      // Should render both conversations
      const items = screen.getAllByRole("button");
      expect(items.length).toBeGreaterThanOrEqual(2);
    });

    it("should render empty message when no conversations", () => {
      render(<ConversationList conversations={[]} onSelect={onSelect} />);

      expect(screen.getByText(/会話履歴がありません/i)).toBeInTheDocument();
    });

    it("should show message count for each conversation", () => {
      render(
        <ConversationList
          conversations={mockConversations}
          onSelect={onSelect}
        />
      );

      // Should show message counts
      expect(screen.getByText(/3/)).toBeInTheDocument();
      expect(screen.getByText(/5/)).toBeInTheDocument();
    });
  });

  describe("selection", () => {
    it("should call onSelect when conversation is clicked", () => {
      render(
        <ConversationList
          conversations={mockConversations}
          onSelect={onSelect}
        />
      );

      const items = screen.getAllByRole("button");
      fireEvent.click(items[0]);

      expect(onSelect).toHaveBeenCalledWith("conv-1");
    });

    it("should highlight selected conversation", () => {
      render(
        <ConversationList
          conversations={mockConversations}
          selectedId="conv-1"
          onSelect={onSelect}
        />
      );

      // Selected item should have different styling
      const selectedItem = screen.getByTestId("conversation-conv-1");
      expect(selectedItem).toHaveAttribute("data-selected", "true");
    });
  });

  describe("loading state", () => {
    it("should show loading indicator when isLoading is true", () => {
      render(
        <ConversationList
          conversations={[]}
          onSelect={onSelect}
          isLoading={true}
        />
      );

      expect(screen.getByText(/読み込み中/i)).toBeInTheDocument();
    });
  });

  describe("deletion", () => {
    it("should call onDelete when delete button is clicked", () => {
      render(
        <ConversationList
          conversations={mockConversations}
          onSelect={onSelect}
          onDelete={onDelete}
        />
      );

      const deleteButtons = screen.getAllByLabelText(/削除/i);
      fireEvent.click(deleteButtons[0]);

      expect(onDelete).toHaveBeenCalledWith("conv-1");
    });

    it("should not show delete buttons when onDelete is not provided", () => {
      render(
        <ConversationList
          conversations={mockConversations}
          onSelect={onSelect}
        />
      );

      const deleteButtons = screen.queryAllByLabelText(/削除/i);
      expect(deleteButtons).toHaveLength(0);
    });
  });
});
