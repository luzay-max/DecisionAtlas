import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { LanguageToggle } from "../components/i18n/language-toggle";
import { LanguageProvider } from "../components/i18n/language-provider";

describe("language toggle", () => {
  it("switches between English and Chinese", async () => {
    const user = userEvent.setup();

    render(
      <LanguageProvider>
        <LanguageToggle />
      </LanguageProvider>
    );

    expect(screen.getByText("EN")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Language" }));

    await waitFor(() => {
      expect(screen.getByText("中文")).toBeInTheDocument();
    });
  });
});
