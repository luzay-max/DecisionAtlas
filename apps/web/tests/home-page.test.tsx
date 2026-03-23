import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import HomePage from "../app/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    refresh: vi.fn(),
  }),
}));

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    getProviderMode: vi.fn().mockResolvedValue({
      mode: "fake",
      is_live: false,
      llm_provider_mode: "fake",
      embedding_provider_mode: "fake",
      override_active: true,
    }),
    setProviderMode: vi.fn(),
  };
});

describe("HomePage", () => {
  it("renders the project name and MVP concepts", async () => {
    render(<HomePage />);

    expect(screen.getByText("DecisionAtlas")).toBeInTheDocument();
    expect(screen.getByText(/engineering decision memory/i)).toBeInTheDocument();
    expect(screen.getByText("Import")).toBeInTheDocument();
    expect(screen.getByText("Decisions")).toBeInTheDocument();
    expect(screen.getByText("Why")).toBeInTheDocument();
    expect(screen.getByText(/the guided demo is the primary mvp experience/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /start guided demo/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /jump to review/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /jump to why search/i })).toBeInTheDocument();
    expect(screen.getByText(/seeded walkthrough data with stable outcomes/i)).toBeInTheDocument();
    expect(screen.getByText(/advanced \/ experimental/i)).toBeInTheDocument();
    expect(screen.getByText(/analyze a real public github repository/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /run live analysis/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /use fake for next run/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /use live for next run/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /back to home/i })).toHaveAttribute("href", "/");

    await waitFor(() => {
      expect(screen.getByText("Provider mode: Fake provider")).toBeInTheDocument();
    });
  });
});
