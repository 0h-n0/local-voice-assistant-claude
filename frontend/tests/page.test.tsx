import { render, screen, waitFor } from "@testing-library/react";
import Home from "@/app/page";

// Mock the API module
jest.mock("@/lib/api", () => ({
  getHealth: jest.fn(),
}));

import { getHealth } from "@/lib/api";

const mockGetHealth = getHealth as jest.MockedFunction<typeof getHealth>;

describe("Home Page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the main heading", () => {
    mockGetHealth.mockResolvedValue({
      status: "healthy",
      version: "0.1.0",
      timestamp: "2025-01-01T00:00:00Z",
    });

    render(<Home />);

    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading).toHaveTextContent("Local Voice Assistant");
  });

  it("shows loading state initially", () => {
    mockGetHealth.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<Home />);

    expect(screen.getByText(/checking backend health/i)).toBeInTheDocument();
  });

  it("displays health status when API call succeeds", async () => {
    mockGetHealth.mockResolvedValue({
      status: "healthy",
      version: "0.1.0",
      timestamp: "2025-01-01T00:00:00Z",
    });

    render(<Home />);

    await waitFor(() => {
      expect(screen.getByText("healthy")).toBeInTheDocument();
    });

    expect(screen.getByText(/version: 0\.1\.0/i)).toBeInTheDocument();
  });

  it("displays error message when API call fails", async () => {
    mockGetHealth.mockRejectedValue(new Error("Connection refused"));

    render(<Home />);

    await waitFor(() => {
      expect(screen.getByText(/error: connection refused/i)).toBeInTheDocument();
    });

    expect(
      screen.getByText(/make sure the backend is running/i)
    ).toBeInTheDocument();
  });
});
