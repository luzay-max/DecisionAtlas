import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { LiveAnalysisForm } from "../components/home/live-analysis-form";
import { LanguageProvider } from "../components/i18n/language-provider";

const push = vi.fn();
const startGithubImport = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push,
    refresh: vi.fn(),
  }),
}));

vi.mock("../lib/api", () => ({
  startGithubImport: (...args: unknown[]) => startGithubImport(...args),
}));

describe("LiveAnalysisForm", () => {
  beforeEach(() => {
    push.mockReset();
    startGithubImport.mockReset();
  });

  it("starts live analysis and redirects to the imported workspace", async () => {
    const user = userEvent.setup();
    startGithubImport.mockResolvedValue({
      job_id: "job-live",
      workspace_slug: "github-org-repo",
      repo: "org/repo",
      status: "queued",
      imported_count: 0,
      summary: { stage: "queued" },
    });

    render(
      <LanguageProvider>
        <LiveAnalysisForm />
      </LanguageProvider>
    );

    await user.type(screen.getByLabelText("Repository"), "org/repo");
    await user.click(screen.getByRole("button", { name: "Run live analysis" }));

    await waitFor(() => {
      expect(startGithubImport).toHaveBeenCalledWith(null, "org/repo");
    });
    expect(push).toHaveBeenCalledWith("/workspaces/github-org-repo");
  });
});
