"use client";

import React, { useState } from "react";

import { getImportJob, startGithubImport } from "../../lib/api";

export function DemoImportButton({ workspaceSlug, repo }: { workspaceSlug: string; repo: string }) {
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function waitForJob(jobId: string) {
    for (let attempt = 0; attempt < 8; attempt += 1) {
      const job = await getImportJob(jobId);
      if (job.status === "failed" || job.status === "succeeded") {
        return job;
      }
      setMessage(`Import ${job.status ?? "running"}...`);
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    return null;
  }

  async function handleClick() {
    setLoading(true);
    setMessage("Queued demo import...");
    try {
      setMessage("Running demo import...");
      const response = await startGithubImport(workspaceSlug, repo);
      const job = await waitForJob(response.job_id);
      if (job === null) {
        setMessage("Import started in background. Refresh the dashboard in a bit to see the result.");
        return;
      }
      if (job.status === "failed") {
        setMessage(`Import failed: ${job.error_message ?? "unknown error"}`);
        return;
      }
      setMessage(`Imported ${job.imported_count} artifacts from ${job.repo ?? repo}`);
    } catch (error) {
      const detail = error instanceof Error ? error.message : "unknown error";
      setMessage(`Import failed: ${detail}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <button type="button" onClick={handleClick}>
        {loading ? "Importing..." : "Run Demo Import"}
      </button>
      <p>Repo: {repo}</p>
      {message ? <p>{message}</p> : null}
    </div>
  );
}
