"use client";

import React, { useState } from "react";

import { getImportJob, startGithubImport } from "../../lib/api";

export function DemoImportButton({ workspaceSlug, repo }: { workspaceSlug: string; repo: string }) {
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    setMessage("Queued demo import...");
    try {
      setMessage("Running demo import...");
      const response = await startGithubImport(workspaceSlug, repo);
      const job = await getImportJob(response.job_id);
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
