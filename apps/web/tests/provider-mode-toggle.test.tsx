import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { ProviderModeToggle } from "../components/runtime/provider-mode-toggle";
import { LanguageProvider } from "../components/i18n/language-provider";

const getProviderMode = vi.fn();
const setProviderMode = vi.fn();

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    getProviderMode: (...args: unknown[]) => getProviderMode(...args),
    setProviderMode: (...args: unknown[]) => setProviderMode(...args),
  };
});

describe("ProviderModeToggle", () => {
  beforeEach(() => {
    getProviderMode.mockReset();
    setProviderMode.mockReset();
  });

  it("loads the current provider mode and switches to live", async () => {
    const user = userEvent.setup();
    getProviderMode.mockResolvedValue({
      mode: "fake",
      is_live: false,
      llm_provider_mode: "fake",
      embedding_provider_mode: "fake",
      override_active: true,
    });
    setProviderMode.mockResolvedValue({
      mode: "openai_compatible",
      is_live: true,
      llm_provider_mode: "openai_compatible",
      embedding_provider_mode: "openai_compatible",
      override_active: true,
    });

    render(
      <LanguageProvider>
        <ProviderModeToggle />
      </LanguageProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Provider mode: Fake provider")).toBeInTheDocument();
    });
    expect(
      screen.getByText(
        "This only affects the next live analysis or future extraction run. It does not rewrite the workspace results already on screen."
      )
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Back to home" })).toHaveAttribute("href", "/");

    await user.click(screen.getByRole("button", { name: "Use live for next run" }));

    await waitFor(() => {
      expect(setProviderMode).toHaveBeenCalledWith("live");
    });
    await waitFor(() => {
      expect(screen.getByText("Provider mode: Live provider")).toBeInTheDocument();
    });
  });
});
