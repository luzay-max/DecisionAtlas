import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import EvidencePage from "../app/evidence/page";

vi.mock("next/navigation", () => ({
  usePathname: () => "/evidence",
}));

vi.mock("../../components/i18n/language-provider", () => ({
  useI18n: () => ({
    messages: {
      nav: { home: "Home" },
      governance: { title: "Governance" },
    },
  }),
}));

vi.mock("../../components/navigation/global-sidebar", () => ({
  GlobalSidebar: () => <aside data-testid="global-sidebar" />,
}));

vi.mock("../../components/auth/session-provider", () => ({
  ProductSessionProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("../../components/theme/theme-provider", () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe("EvidencePage", () => {
  it("renders evidence dashboard with reports section", () => {
    render(<EvidencePage />);
    expect(screen.getByText("Evidence Dashboard")).toBeTruthy();
    expect(screen.getByText("Available Reports")).toBeTruthy();
    expect(screen.getByText("Self-Hosted Package")).toBeTruthy();
  });

  it("shows loading state initially", () => {
    render(<EvidencePage />);
    expect(screen.getByText("Loading evidence...")).toBeTruthy();
  });
});
