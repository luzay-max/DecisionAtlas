import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { LiveAnalysisForm } from "../components/home/live-analysis-form";
import { LanguageProvider } from "../components/i18n/language-provider";

const push = vi.fn();
const startGithubImport = vi.fn();
const lookupGithubImport = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push,
    refresh: vi.fn(),
  }),
}));

vi.mock("../lib/api", () => ({
  lookupGithubImport: (...args: unknown[]) => lookupGithubImport(...args),
  startGithubImport: (...args: unknown[]) => startGithubImport(...args),
}));

describe("LiveAnalysisForm", () => {
  beforeEach(() => {
    push.mockReset();
    startGithubImport.mockReset();
    lookupGithubImport.mockReset();
    lookupGithubImport.mockResolvedValue({
      repo: "org/repo",
      repo_url: "https://github.com/org/repo",
      workspace_exists: false,
      workspace_slug: null,
      has_successful_import: false,
      can_incremental_sync: false,
      has_running_import: false,
      latest_import: null,
    });
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
    await waitFor(() => {
      expect(lookupGithubImport).toHaveBeenCalledWith("org/repo");
    });
    await user.click(screen.getByRole("button", { name: "Run live analysis" }));

    await waitFor(() => {
      expect(startGithubImport).toHaveBeenCalledWith(null, "org/repo", "full");
    });
    expect(push).toHaveBeenCalledWith("/workspaces/github-org-repo");
  });

  it("shows existing workspace controls and allows incremental sync", async () => {
    const user = userEvent.setup();
    lookupGithubImport.mockResolvedValue({
      repo: "org/repo",
      repo_url: "https://github.com/org/repo",
      workspace_exists: true,
      workspace_slug: "github-org-repo",
      has_successful_import: true,
      can_incremental_sync: true,
      has_running_import: false,
      latest_import: {
        job_id: "job-old",
        workspace_slug: "github-org-repo",
        repo: "org/repo",
        mode: "full",
        status: "succeeded",
        imported_count: 12,
      },
    });
    startGithubImport.mockResolvedValue({
      job_id: "job-sync",
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

    await waitFor(() => {
      expect(screen.getByText("Existing imported workspace found")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Sync since last import" }));

    await waitFor(() => {
      expect(startGithubImport).toHaveBeenCalledWith("github-org-repo", "org/repo", "since_last_sync");
    });
    expect(push).toHaveBeenCalledWith("/workspaces/github-org-repo");
  });
});
