import React from "react";
import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { DemoImportButton } from "../components/dashboard/demo-import-button";
import { LanguageProvider } from "../components/i18n/language-provider";

const refresh = vi.fn();
const startGithubImport = vi.fn();
const getImportJob = vi.fn();
const pauseGithubImport = vi.fn();
const resumeGithubImport = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh,
  }),
}));

vi.mock("../lib/api", () => ({
  startGithubImport: (...args: unknown[]) => startGithubImport(...args),
  getImportJob: (...args: unknown[]) => getImportJob(...args),
  pauseGithubImport: (...args: unknown[]) => pauseGithubImport(...args),
  resumeGithubImport: (...args: unknown[]) => resumeGithubImport(...args),
}));

describe("DemoImportButton", () => {
  beforeEach(() => {
    vi.useRealTimers();
    refresh.mockReset();
    startGithubImport.mockReset();
    getImportJob.mockReset();
    pauseGithubImport.mockReset();
    resumeGithubImport.mockReset();
  });


  it("waits for a confirmed pause, disables duplicate clicks, and then shows resume", async () => {
    const user = userEvent.setup();
    // Keep background polling isolated; this test drives only the control action.
    getImportJob.mockImplementation(() => new Promise(() => {}));
    let confirmPause: ((value: { job_id: string; status: string; summary: { stage: string } }) => void) | undefined;
    pauseGithubImport.mockImplementation(
      () => new Promise((resolve) => { confirmPause = resolve; })
    );
    render(
      <LanguageProvider>
        <DemoImportButton
          workspaceSlug="github-org-repo"
          repo="org/repo"
          latestImport={{
            job_id: "job-running",
            mode: "full",
            status: "running",
            imported_count: 0,
            summary: { stage: "importing_artifacts" },
            error_message: null,
            started_at: null,
            finished_at: null,
          }}
        />
      </LanguageProvider>
    );

    const pauseButton = screen.getByRole("button", { name: /暂停 \(Pause\)/ });
    await user.click(pauseButton);
    expect(pauseGithubImport).toHaveBeenCalledExactlyOnceWith("job-running");
    expect(pauseButton).toBeDisabled();
    expect(screen.queryByRole("button", { name: /恢复 \(Resume\)/ })).not.toBeInTheDocument();
    await user.click(pauseButton);
    expect(pauseGithubImport).toHaveBeenCalledTimes(1);

    await act(async () => {
      confirmPause?.({ job_id: "job-running", status: "paused", summary: { stage: "importing_artifacts" } });
    });
    expect(screen.getByRole("button", { name: /恢复 \(Resume\)/ })).toBeEnabled();
    expect(refresh).toHaveBeenCalled();
  });

  it("shows a failed pause without falsely marking the import as paused", async () => {
    const user = userEvent.setup();
    getImportJob.mockImplementation(() => new Promise(() => {}));
    pauseGithubImport.mockRejectedValue(new Error("Forbidden"));
    render(
      <LanguageProvider>
        <DemoImportButton
          workspaceSlug="github-org-repo"
          repo="org/repo"
          latestImport={{
            job_id: "job-running",
            mode: "full",
            status: "running",
            imported_count: 0,
            summary: { stage: "importing_artifacts" },
            error_message: null,
            started_at: null,
            finished_at: null,
          }}
        />
      </LanguageProvider>
    );

    await user.click(screen.getByRole("button", { name: /暂停 \(Pause\)/ }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Forbidden");
    expect(screen.getByRole("button", { name: /暂停 \(Pause\)/ })).toBeEnabled();
    expect(screen.queryByRole("button", { name: /恢复 \(Resume\)/ })).not.toBeInTheDocument();
    expect(refresh).not.toHaveBeenCalled();
  });

  it("shows running only after resume confirmation", async () => {
    const user = userEvent.setup();
    getImportJob.mockImplementation(() => new Promise(() => {}));
    resumeGithubImport.mockResolvedValue({
      job_id: "job-paused",
      status: "running",
      summary: { stage: "extracting_decisions" },
    });
    render(
      <LanguageProvider>
        <DemoImportButton
          workspaceSlug="github-org-repo"
          repo="org/repo"
          latestImport={{
            job_id: "job-paused",
            mode: "full",
            status: "paused",
            imported_count: 0,
            summary: { stage: "extracting_decisions" },
            error_message: null,
            started_at: null,
            finished_at: null,
          }}
        />
      </LanguageProvider>
    );
    await user.click(screen.getByRole("button", { name: /恢复 \(Resume\)/ }));
    expect(resumeGithubImport).toHaveBeenCalledWith("job-paused");
    expect(await screen.findByRole("button", { name: /暂停 \(Pause\)/ })).toBeEnabled();
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

    await user.click(screen.getByRole("button", { name: "Run import" }));

    await waitFor(() => {
      expect(screen.getAllByText("Imported 11 artifacts from encode/httpx").length).toBeGreaterThan(0);
    });
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "100");
    expect(refresh).toHaveBeenCalledTimes(1);
  });

  it("disables the button while an import is running", async () => {
    const user = userEvent.setup();
    let resolveImport: ((value: { job_id: string }) => void) | undefined;
    getImportJob
      .mockResolvedValueOnce({
        job_id: "job-123",
        status: "running",
        imported_count: 0,
        summary: { stage: "queued" },
        repo: "encode/httpx",
      })
      .mockResolvedValue({
        job_id: "job-123",
        status: "succeeded",
        imported_count: 1,
        summary: { stage: "completed" },
        repo: "encode/httpx",
      });
    startGithubImport.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveImport = resolve;
        })
    );

    render(
      <LanguageProvider>
        <DemoImportButton workspaceSlug="demo-workspace" repo="encode/httpx" />
      </LanguageProvider>
    );

    const button = screen.getByRole("button", { name: "Run import" });
    await user.click(button);

    expect(startGithubImport).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("button", { name: "Importing..." })).toBeDisabled();

    await act(async () => {
      resolveImport?.({ job_id: "job-123" });
    });
  });

  it("continues polling an existing running import when the page loads mid-flight", async () => {
    getImportJob
      .mockResolvedValueOnce({
        job_id: "job-running",
        status: "running",
        summary: { stage: "indexing_artifacts" },
        imported_count: 0,
        repo: "encode/httpx",
      })
      .mockResolvedValueOnce({
        job_id: "job-running",
        status: "succeeded",
        imported_count: 7,
        repo: "encode/httpx",
        summary: { stage: "completed" },
      })
      .mockResolvedValue({
        job_id: "job-running",
        status: "succeeded",
        imported_count: 7,
        repo: "encode/httpx",
        summary: { stage: "completed" },
      });

    render(
      <LanguageProvider>
        <DemoImportButton
          workspaceSlug="demo-workspace"
          repo="encode/httpx"
          importStatus="running"
          latestImport={{
            job_id: "job-running",
            mode: "full",
            status: "running",
            imported_count: 0,
            summary: { stage: "indexing_artifacts" },
            error_message: null,
            started_at: null,
            finished_at: null,
          }}
        />
      </LanguageProvider>
    );

    await waitFor(() => {
      expect(screen.getAllByText(/Import indexing artifacts/i).length).toBeGreaterThan(0);
    });
    await waitFor(() => {
      expect(screen.getAllByText("Imported 7 artifacts from encode/httpx").length).toBeGreaterThan(0);
    });
    expect(screen.getByText(/Import job: job-running/i)).toBeInTheDocument();
  });

  it("shows extraction progress details and eta while extracting decisions", () => {
    render(
      <LanguageProvider>
        <DemoImportButton
          workspaceSlug="github-org-repo"
          repo="org/repo"
          importStatus="running"
          latestImport={{
            job_id: "job-extracting",
            mode: "full",
            status: "running",
            imported_count: 0,
            summary: {
              stage: "extracting_decisions",
              extraction_summary: {
                shortlisted_artifacts: 12,
                screened_artifacts: 8,
                screened_in_artifacts: 5,
                screened_out_artifacts: 3,
                full_extraction_requests: 5,
                completed_full_extractions: 1,
                total_artifacts: 20,
                processed_artifacts: 5,
                created_candidates: 1,
                skipped_provider_400: 0,
                skipped_provider_timeout: 1,
                skipped_invalid_json: 0,
                elapsed_seconds: 25,
                estimated_remaining_seconds: 75,
                current_artifact_title: "Architecture RFC",
                current_phase: "extracting",
              },
            },
            error_message: null,
            started_at: null,
            finished_at: null,
          }}
        />
      </LanguageProvider>
    );

    expect(screen.getByText("Processed 5 of 20 extraction items.")).toBeInTheDocument();
    expect(screen.getByText("Current extraction phase: full extraction.")).toBeInTheDocument();
    expect(screen.getByText("Screened 8 of 12 shortlisted artifacts.")).toBeInTheDocument();
    expect(screen.getByText("Completed 1 of 5 full extraction requests.")).toBeInTheDocument();
    expect(screen.getByText("Estimated time remaining: 1m 15s.")).toBeInTheDocument();
    expect(screen.getByText("Current artifact: Architecture RFC")).toBeInTheDocument();
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "81");
  });

  it("starts polling from an initial job id before latest import appears on the page", async () => {
    getImportJob
      .mockResolvedValueOnce({
        job_id: "job-from-query",
        status: "running",
        imported_count: 0,
        repo: "psf/requests",
        summary: { stage: "indexing_artifacts" },
      })
      .mockResolvedValueOnce({
        job_id: "job-from-query",
        status: "succeeded",
        imported_count: 1154,
        repo: "psf/requests",
        summary: { stage: "completed" },
      });

    render(
      <LanguageProvider>
        <DemoImportButton workspaceSlug="github-psf-requests" repo="psf/requests" importStatus="ready" initialJobId="job-from-query" />
      </LanguageProvider>
    );

    await waitFor(() => {
      expect(getImportJob).toHaveBeenCalledWith("job-from-query");
    });
    await waitFor(() => {
      expect(screen.getAllByText("Imported 1154 artifacts from psf/requests").length).toBeGreaterThan(0);
    });
    expect(screen.getByText(/Import job: job-from-query/i)).toBeInTheDocument();
  });

  it("keeps polling long-running imports until the job completes", async () => {
    vi.useFakeTimers();
    let pollCount = 0;
    getImportJob.mockImplementation(async () => {
      pollCount += 1;
      if (pollCount <= 24) {
        return {
          job_id: "job-long-running",
          status: "running",
          imported_count: 0,
          repo: "psf/requests",
          summary: { stage: "importing_artifacts" },
        };
      }
      return {
        job_id: "job-long-running",
        status: "succeeded",
        imported_count: 1202,
        repo: "psf/requests",
        summary: { stage: "completed" },
      };
    });

    render(
      <LanguageProvider>
        <DemoImportButton workspaceSlug="github-psf-requests" repo="psf/requests" importStatus="ready" initialJobId="job-long-running" />
      </LanguageProvider>
    );

    await act(async () => {
      await vi.advanceTimersByTimeAsync(12000);
    });

    expect(screen.getAllByText("Imported 1202 artifacts from psf/requests").length).toBeGreaterThan(0);
    expect(getImportJob).toHaveBeenCalledTimes(25);
  });
});
