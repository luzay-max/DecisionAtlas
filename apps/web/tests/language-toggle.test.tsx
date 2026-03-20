import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import HomePage from "../app/page";
import { LanguageProvider } from "../components/i18n/language-provider";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    refresh: vi.fn(),
  }),
}));

describe("language toggle", () => {
  it("switches the homepage between English and Chinese", async () => {
    const user = userEvent.setup();

    render(
      <LanguageProvider>
        <HomePage />
      </LanguageProvider>
    );

    expect(screen.getByText("Engineering decision memory with citations.")).toBeInTheDocument();
    expect(document.documentElement.lang).toBe("en");

    await user.click(screen.getByRole("button", { name: "Language" }));

    await waitFor(() => {
      expect(screen.getByText("带引用的工程决策记忆。")).toBeInTheDocument();
      expect(document.documentElement.lang).toBe("zh");
    });
  });
});
