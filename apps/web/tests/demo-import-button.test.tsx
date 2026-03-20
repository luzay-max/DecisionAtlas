import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { DemoImportButton } from "../components/dashboard/demo-import-button";
import { LanguageProvider } from "../components/i18n/language-provider";

const refresh = vi.fn();
const startGithubImport = vi.fn();
const getImportJob = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh,
  }),
}));

vi.mock("../lib/api", () => ({
  startGithubImport: (...args: unknown[]) => startGithubImport(...args),
  getImportJob: (...args: unknown[]) => getImportJob(...args),
}));

describe("DemoImportButton", () => {
  beforeEach(() => {
    refresh.mockReset();
    startGithubImport.mockReset();
    getImportJob.mockReset();
  });

  it("refreshes the dashboard after a successful import job completes", async () => {
    const user = userEvent.setup();
    startGithubImport.mockResolvedValue({
      job_id: "job-123",
    });
    getImportJob.mockResolvedValue({
      status: "succeeded",
      imported_count: 11,
      repo: "encode/httpx",
    });

    render(
      <LanguageProvider>
        <DemoImportButton workspaceSlug="demo-workspace" repo="encode/httpx" />
      </LanguageProvider>
    );

    await user.click(screen.getByRole("button", { name: "Run Demo Import" }));

    await waitFor(() => {
      expect(screen.getByText("Imported 11 artifacts from encode/httpx")).toBeInTheDocument();
    });
    expect(refresh).toHaveBeenCalledTimes(1);
  });
});
