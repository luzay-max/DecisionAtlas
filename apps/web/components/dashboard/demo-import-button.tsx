"use client";

import Link from "next/link";
import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { DashboardSummary, ImportSummary, getImportJob, startGithubImport } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

const progressStages = ["queued", "importing_artifacts", "indexing_artifacts", "extracting_decisions", "completed"] as const;

export function DemoImportButton({
  workspaceSlug,
  repo,
  latestImport,
  importStatus,
}: {
  workspaceSlug: string;
  repo: string;
  latestImport?: DashboardSummary["latest_import"];
  importStatus?: string;
}) {
  const { messages } = useI18n();
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [nextMessage, setNextMessage] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<string | null>(latestImport?.summary?.stage ?? importStatus ?? null);
  const [loading, setLoading] = useState(false);
  const [activeJobId, setActiveJobId] = useState<string | null>(latestImport?.job_id ?? null);
  const [jobStatus, setJobStatus] = useState<string | null>(latestImport?.status ?? importStatus ?? null);
  const [progressMessage, setProgressMessage] = useState<string | null>(null);
  const [progressDetails, setProgressDetails] = useState<string[]>([]);
  const [activeExtractionSummary, setActiveExtractionSummary] = useState(latestImport?.summary?.extraction_summary ?? null);
  const pollingRef = useRef(false);

  const activeStage = currentStage ?? jobStatus ?? "queued";
  const activeIndex = Math.max(progressStages.indexOf((activeStage as (typeof progressStages)[number]) ?? "queued"), 0);
  const extractionSummary = activeExtractionSummary;
  const progressPercent = (() => {
    if (activeStage === "extracting_decisions" && jobStatus !== "succeeded") {
      const total = extractionSummary?.total_artifacts ?? 0;
      const processed = extractionSummary?.processed_artifacts ?? 0;
      if (total > 0) {
        return Math.min(99, 75 + Math.round((processed / total) * 24));
      }
    }
    return Math.min(100, Math.round((activeIndex / (progressStages.length - 1)) * 100));
  })();

  function formatEta(seconds: number | null | undefined) {
    if (seconds == null || seconds < 0) {
      return null;
    }
    if (seconds < 60) {
      return `${seconds}s`;
    }
    if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
    }
    const hours = Math.floor(seconds / 3600);
    const remainingMinutes = Math.floor((seconds % 3600) / 60);
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  }

  function buildExtractionDetails(summary?: ImportSummary | null) {
    if (!summary || summary.stage !== "extracting_decisions") {
      return [];
    }
    const extraction = summary.extraction_summary;
    if (!extraction) {
      return [messages.importButton.extractionPreparing];
    }

    const details: string[] = [];
    if (extraction.total_artifacts > 0) {
      details.push(
        messages.importButton.extractionProgress
          .replace("{processed}", String(extraction.processed_artifacts))
          .replace("{total}", String(extraction.total_artifacts))
      );
    } else {
      details.push(messages.importButton.extractionPreparing);
    }

    const eta = formatEta(extraction.estimated_remaining_seconds);
    if (eta) {
      details.push(messages.importButton.extractionEta.replace("{eta}", eta));
    }
    if (extraction.current_artifact_title) {
      details.push(messages.importButton.extractionCurrentArtifact.replace("{title}", extraction.current_artifact_title));
    }
    return details;
  }

  function applyJobState(job: Awaited<ReturnType<typeof getImportJob>>) {
    if (!job) {
      return;
    }
    const stageValue = job.summary?.stage ?? job.status ?? "queued";
    const stageIndex = Math.max(progressStages.indexOf((stageValue as (typeof progressStages)[number]) ?? "queued"), 0);
    const translatedStage = job.summary?.stage
      ? (messages.status[job.summary.stage as keyof typeof messages.status] ?? job.summary.stage)
      : (messages.status[job.status as keyof typeof messages.status] ?? job.status ?? "running");
    setActiveJobId(job.job_id);
    setJobStatus(job.status ?? null);
    setCurrentStage(job.summary?.stage ?? job.status ?? null);
    setActiveExtractionSummary(job.summary?.extraction_summary ?? null);
    setProgressDetails(buildExtractionDetails(job.summary ?? null));

    if (job.status === "failed") {
      setMessage(messages.importButton.failed.replace("{detail}", job.error_message ?? "unknown error"));
      setNextMessage(messages.importButton.failedNext);
      setProgressMessage(messages.importButton.failedHint);
      return;
    }

    if (job.status === "succeeded") {
      setCurrentStage("completed");
      setMessage(
        messages.importButton.imported
          .replace("{count}", String(job.imported_count))
          .replace("{repo}", job.repo ?? repo)
      );
      setNextMessage(messages.importButton.importedNext);
      setProgressMessage(messages.importButton.completedHint);
      return;
    }

    setMessage(messages.importButton.stageRunning.replace("{stage}", translatedStage));
    setProgressMessage(
      messages.importButton.progressHint
        .replace("{step}", String(Math.min(stageIndex + 1, progressStages.length - 1)))
        .replace("{total}", String(progressStages.length - 1))
    );
  }

  async function waitForJob(jobId: string) {
    pollingRef.current = true;
    for (let attempt = 0; attempt < 20; attempt += 1) {
      const job = await getImportJob(jobId);
      if (!job) {
        pollingRef.current = false;
        return null;
      }
      applyJobState(job);
      if (job.status === "failed" || job.status === "succeeded") {
        pollingRef.current = false;
        return job;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    pollingRef.current = false;
    return null;
  }

  async function handleClick() {
    if (loading) {
      return;
    }
    setLoading(true);
    setActiveJobId(null);
    setJobStatus("queued");
    setCurrentStage("queued");
    setMessage(messages.importButton.queued);
    setProgressMessage(messages.importButton.progressHint.replace("{step}", "1").replace("{total}", String(progressStages.length - 1)));
    setActiveExtractionSummary(null);
    setProgressDetails([]);
    setNextMessage(null);
    try {
      setMessage(messages.importButton.running);
      const response = await startGithubImport(workspaceSlug, repo);
      setActiveJobId(response.job_id);
      const job = await waitForJob(response.job_id);
      if (job === null) {
        setMessage(messages.importButton.background);
        setNextMessage(messages.importButton.backgroundNext);
        setProgressMessage(messages.importButton.backgroundHint);
        router.refresh();
        return;
      }
      router.refresh();
    } catch (error) {
      const detail = error instanceof Error ? error.message : "unknown error";
      setMessage(messages.importButton.failed.replace("{detail}", detail));
      setNextMessage(messages.importButton.failedNext);
      setProgressMessage(messages.importButton.failedHint);
      router.refresh();
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!latestImport) {
      setMessage(null);
      setProgressMessage(null);
      setActiveExtractionSummary(null);
      setProgressDetails([]);
      return;
    }
    if (latestImport.status === "succeeded") {
      setCurrentStage("completed");
      setJobStatus("succeeded");
      setActiveExtractionSummary(latestImport.summary?.extraction_summary ?? null);
      setMessage(
        messages.importButton.imported
          .replace("{count}", String(latestImport.imported_count))
          .replace("{repo}", latestImport.repo ?? repo)
      );
      setProgressMessage(messages.importButton.completedHint);
      setProgressDetails([]);
      return;
    }
    if (latestImport.status === "failed") {
      setJobStatus("failed");
      setCurrentStage(latestImport.summary?.stage ?? "queued");
      setActiveExtractionSummary(latestImport.summary?.extraction_summary ?? null);
      setMessage(messages.importButton.failed.replace("{detail}", latestImport.error_message ?? "unknown error"));
      setProgressMessage(messages.importButton.failedHint);
      setProgressDetails(buildExtractionDetails(latestImport.summary ?? null));
      return;
    }
    setActiveExtractionSummary(latestImport.summary?.extraction_summary ?? null);
    setProgressDetails(buildExtractionDetails(latestImport.summary ?? null));
  }, [latestImport, messages, repo]);

  useEffect(() => {
    if (!activeJobId || pollingRef.current) {
      return;
    }
    if (jobStatus !== "queued" && jobStatus !== "running") {
      return;
    }
    void waitForJob(activeJobId).then(() => {
      router.refresh();
    });
  }, [activeJobId, jobStatus, router]);

  return (
    <div className="stack import-status-shell">
      <button type="button" onClick={handleClick} disabled={loading}>
        {loading ? messages.importButton.importing : messages.importButton.runDemoImport}
      </button>
      <p>
        {messages.importButton.repoLabel} {repo}
      </p>
      <div className="card stack import-progress-card" aria-live="polite">
        <div className="import-progress-head">
          <div className="import-progress-status">
            {jobStatus === "queued" || jobStatus === "running" ? <span className="spinner" aria-hidden="true" /> : null}
            <strong>{message ?? messages.importButton.idle}</strong>
          </div>
          <span>{progressPercent}%</span>
        </div>
        <div className="import-progress-bar" role="progressbar" aria-valuenow={progressPercent} aria-valuemin={0} aria-valuemax={100}>
          <span className="import-progress-bar-fill" style={{ width: `${progressPercent}%` }} />
        </div>
        {progressMessage ? <p className="guided-demo-status">{progressMessage}</p> : null}
        {progressDetails.map((detail) => (
          <p key={detail} className="guided-demo-status">
            {detail}
          </p>
        ))}
        {activeJobId ? <p className="guided-demo-status">{messages.importButton.jobLabel.replace("{jobId}", activeJobId)}</p> : null}
      </div>
      <ol className="guided-demo-step-list import-progress-list">
        {progressStages.map((stage) => {
          const stageIndex = progressStages.indexOf(stage);
          const className =
            activeStage === stage
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
