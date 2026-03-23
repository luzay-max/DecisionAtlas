"use client";

import Link from "next/link";
import React, { useState } from "react";
import { useRouter } from "next/navigation";

import { getImportJob, startGithubImport } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function DemoImportButton({ workspaceSlug, repo }: { workspaceSlug: string; repo: string }) {
  const { messages } = useI18n();
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [nextMessage, setNextMessage] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function waitForJob(jobId: string) {
    for (let attempt = 0; attempt < 20; attempt += 1) {
      const job = await getImportJob(jobId);
      if (job.status === "failed" || job.status === "succeeded") {
        return job;
      }
      const stage = job.summary?.stage
        ? (messages.status[job.summary.stage as keyof typeof messages.status] ?? job.summary.stage)
        : (messages.status[job.status as keyof typeof messages.status] ?? job.status ?? "running");
      setCurrentStage(job.summary?.stage ?? job.status ?? null);
      setMessage(messages.importButton.stageRunning.replace("{stage}", stage));
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    return null;
  }

  async function handleClick() {
    if (loading) {
      return;
    }
    setLoading(true);
    setCurrentStage("queued");
    setMessage(messages.importButton.queued);
    setNextMessage(null);
    try {
      setMessage(messages.importButton.running);
      const response = await startGithubImport(workspaceSlug, repo);
      const job = await waitForJob(response.job_id);
      if (job === null) {
        setMessage(messages.importButton.background);
        setNextMessage(messages.importButton.backgroundNext);
        router.refresh();
        return;
      }
      if (job.status === "failed") {
        setMessage(messages.importButton.failed.replace("{detail}", job.error_message ?? "unknown error"));
        setNextMessage(messages.importButton.failedNext);
        router.refresh();
        return;
      }
      setCurrentStage("completed");
      setMessage(
        messages.importButton.imported
          .replace("{count}", String(job.imported_count))
          .replace("{repo}", job.repo ?? repo)
      );
      setNextMessage(messages.importButton.importedNext);
      router.refresh();
    } catch (error) {
      const detail = error instanceof Error ? error.message : "unknown error";
      setMessage(messages.importButton.failed.replace("{detail}", detail));
      setNextMessage(messages.importButton.failedNext);
      router.refresh();
    } finally {
      setLoading(false);
    }
  }

  const progressStages = ["queued", "importing_artifacts", "indexing_artifacts", "extracting_decisions", "completed"];

  return (
    <div className="stack">
      <button type="button" onClick={handleClick} disabled={loading}>
        {loading ? messages.importButton.importing : messages.importButton.runDemoImport}
      </button>
      <p>
        {messages.importButton.repoLabel} {repo}
      </p>
      <ol className="guided-demo-step-list import-progress-list">
        {progressStages.map((stage) => {
          const activeIndex = progressStages.indexOf(currentStage ?? "queued");
          const stageIndex = progressStages.indexOf(stage);
          const className =
            currentStage === stage
              ? "guided-demo-step active"
              : stageIndex < activeIndex
                ? "guided-demo-step completed"
                : "guided-demo-step";
          return (
            <li key={stage} className={className}>
              <span className="guided-demo-step-index">{stageIndex + 1}</span>
              <span>{messages.status[stage as keyof typeof messages.status] ?? stage}</span>
            </li>
          );
        })}
      </ol>
      {message ? <p>{message}</p> : null}
      {nextMessage ? <p className="guided-demo-status">{nextMessage}</p> : null}
      {nextMessage && currentStage === "completed" ? (
        <div className="action-row">
          <Link href={`/review?workspace=${encodeURIComponent(workspaceSlug)}`} className="action-link action-link-primary">
            {messages.dashboard.reviewCandidates}
          </Link>
        </div>
      ) : null}
    </div>
  );
}
