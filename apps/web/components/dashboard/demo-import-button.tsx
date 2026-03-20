"use client";

"use client";

import React, { useState } from "react";

import { getImportJob, startGithubImport } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function DemoImportButton({ workspaceSlug, repo }: { workspaceSlug: string; repo: string }) {
  const { messages } = useI18n();
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function waitForJob(jobId: string) {
    for (let attempt = 0; attempt < 8; attempt += 1) {
      const job = await getImportJob(jobId);
      if (job.status === "failed" || job.status === "succeeded") {
        return job;
      }
      const status = messages.status[job.status as keyof typeof messages.status] ?? job.status ?? "running";
      setMessage(messages.importButton.statusRunning.replace("{status}", status));
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    return null;
  }

  async function handleClick() {
    setLoading(true);
    setMessage(messages.importButton.queued);
    try {
      setMessage(messages.importButton.running);
      const response = await startGithubImport(workspaceSlug, repo);
      const job = await waitForJob(response.job_id);
      if (job === null) {
        setMessage(messages.importButton.background);
        return;
      }
      if (job.status === "failed") {
        setMessage(messages.importButton.failed.replace("{detail}", job.error_message ?? "unknown error"));
        return;
      }
      setMessage(
        messages.importButton.imported
          .replace("{count}", String(job.imported_count))
          .replace("{repo}", job.repo ?? repo)
      );
    } catch (error) {
      const detail = error instanceof Error ? error.message : "unknown error";
      setMessage(messages.importButton.failed.replace("{detail}", detail));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <button type="button" onClick={handleClick}>
        {loading ? messages.importButton.importing : messages.importButton.runDemoImport}
      </button>
      <p>
        {messages.importButton.repoLabel} {repo}
      </p>
      {message ? <p>{message}</p> : null}
    </div>
  );
}
