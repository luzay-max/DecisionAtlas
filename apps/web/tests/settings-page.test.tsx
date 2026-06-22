import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import SettingsPage from "../app/settings/page";

vi.mock("next/navigation", () => ({
  usePathname: () => "/settings",
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

vi.mock("../../components/runtime/provider-mode-toggle", () => ({
  ProviderModeToggle: () => <div data-testid="provider-toggle" />,
}));

vi.mock("../../components/auth/session-provider", () => ({
  ProductSessionProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("../../components/theme/theme-provider", () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe("SettingsPage", () => {
  it("renders settings page with configuration sections", () => {
    render(<SettingsPage />);
    expect(screen.getByText("Configuration")).toBeTruthy();
    expect(screen.getByText("LLM Provider")).toBeTruthy();
    expect(screen.getByText("System Status")).toBeTruthy();
    expect(screen.getByText("Database")).toBeTruthy();
    expect(screen.getByText("Cache & Queue")).toBeTruthy();
  });
});
