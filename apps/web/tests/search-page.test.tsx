import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { QueryForm } from "../components/search/query-form";

describe("QueryForm", () => {
  it("submits a question and renders citations", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "ok",
        question: "why use redis cache",
        answer: "Use Redis Cache: Use Redis as cache only.",
        citations: [
          {
            quote: "We decided to use Redis as cache",
            url: "https://github.com/org/repo/issues/1"
          }
        ]
      })
    } as Response);

    render(<QueryForm workspaceSlug="demo-workspace" />);
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(screen.getByText("Use Redis Cache: Use Redis as cache only.")).toBeInTheDocument();
    });
    expect(screen.getByText("Status:")).toBeInTheDocument();
    expect(screen.getByText("We decided to use Redis as cache")).toBeInTheDocument();

    global.fetch = originalFetch;
  });

  it("renders a helpful error when why search fails", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      ok: false
    } as Response);

    render(<QueryForm workspaceSlug="demo-workspace" />);
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(screen.getByText(/why search is unavailable right now/i)).toBeInTheDocument();
    });

    global.fetch = originalFetch;
  });
});
