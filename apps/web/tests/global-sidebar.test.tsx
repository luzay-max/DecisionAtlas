import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import { GlobalSidebar } from "../components/navigation/global-sidebar";

vi.mock("next/navigation", () => ({
  usePathname: () => "/review",
}));

vi.mock("../components/i18n/language-provider", () => ({
  useI18n: () => ({
    messages: {
      nav: {
        home: "Home",
        review: "Review",
        search: "Why Search",
        timeline: "Timeline",
        drift: "Drift",
        governance: "Governance",
        team: "Team",
        settings: "Settings",
        evidence: "Evidence",
      },
      governance: { title: "Governance" },
    },
  }),
}));

vi.mock("../components/auth/account-scope-surface", () => ({
  AccountScopeSurface: () => <div data-testid="account-scope" />,
}));

vi.mock("../components/i18n/language-toggle", () => ({
  LanguageToggle: () => <div data-testid="language-toggle" />,
}));

vi.mock("../components/theme/theme-toggle", () => ({
  ThemeToggle: () => <div data-testid="theme-toggle" />,
}));

describe("GlobalSidebar", () => {
  it("renders all navigation links", () => {
    render(<GlobalSidebar />);
    expect(screen.getByText("DecisionAtlas")).toBeTruthy();
    expect(screen.getByText("Home")).toBeTruthy();
    expect(screen.getByText("Review")).toBeTruthy();
    expect(screen.getByText("Why Search")).toBeTruthy();
    expect(screen.getByText("Timeline")).toBeTruthy();
    expect(screen.getByText("Drift")).toBeTruthy();
    expect(screen.getByText("Settings")).toBeTruthy();
    expect(screen.getByText("Evidence")).toBeTruthy();
  });

  it("highlights the active navigation link", () => {
    render(<GlobalSidebar />);
    const reviewLink = screen.getByText("Review").closest("a");
    expect(reviewLink?.className).toContain("active");
  });

  it("renders account scope and theme controls", () => {
    render(<GlobalSidebar />);
    expect(screen.getByTestId("account-scope")).toBeTruthy();
    expect(screen.getByTestId("theme-toggle")).toBeTruthy();
  });
});
