"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { lookupGithubImport, type ImportLookup, startGithubImport } from "../../lib/api";
import { accessRequirementCopy, accessSourceStatusLabel } from "../access-source/access-source-status";
import { useI18n } from "../i18n/language-provider";
import { syncSummary } from "../sync/sync-provenance";

const GITHUB_REPO_INPUT = /^(?:https:\/\/github\.com\/)?[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/?$/i;

export function LiveAnalysisForm() {
  const { messages } = useI18n();
  const router = useRouter();
  const [repo, setRepo] = useState("");
  const [touched, setTouched] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [lookup, setLookup] = useState<ImportLookup | null>(null);
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupFailed, setLookupFailed] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const trimmedRepo = repo.trim();
  const validRepo = GITHUB_REPO_INPUT.test(trimmedRepo);
  const showInvalidRepo = touched && trimmedRepo.length > 0 && !validRepo;
  const existing = Boolean(lookup?.workspace_exists && lookup.workspace_slug);
  const canCreate = validRepo && Boolean(lookup) && !existing && !lookupLoading && !lookupFailed && !loading;

  useEffect(() => {
    if (!validRepo) {
      setLookup(null);
      setLookupFailed(false);
      setLookupLoading(false);
      return;
    }

    let cancelled = false;
    setLookup(null);
    setLookupFailed(false);
    setLookupLoading(true);
    const timeout = setTimeout(async () => {
      try {
        const result = await lookupGithubImport(trimmedRepo);
        if (!cancelled) {
          setLookup(result);
        }
      } catch {
        if (!cancelled) {
          setLookup(null);
          setLookupFailed(true);
        }
      } finally {
        if (!cancelled) {
          setLookupLoading(false);
        }
      }
    }, 350);

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [trimmedRepo, validRepo, retryCount]);

  function workspaceHref(workspaceSlug: string, jobId?: string | null) {
    const base = `/workspaces/${encodeURIComponent(workspaceSlug)}`;
    return jobId ? `${base}?job=${encodeURIComponent(jobId)}` : base;
  }

  const latestLookupSyncSummary = syncSummary(messages, lookup?.latest_import);
  const lookupAccessStatus = accessSourceStatusLabel(messages, lookup?.access_source_status);
  const lookupAccessRequirement = accessRequirementCopy(messages, lookup?.access_requirement);

  async function startImport(mode: "full" | "since_last_sync", workspaceSlug: string | null) {
    if (loading || lookupFailed || lookupLoading || !validRepo) return;
    setLoading(true);
    setActionError(false);
    setMessage(mode === "since_last_sync" ? messages.liveAnalysis.syncSubmitting : messages.liveAnalysis.submitting);
    try {
      const result = await startGithubImport(workspaceSlug, trimmedRepo, mode);
      if (!result.workspace_slug) throw new Error("Missing workspace slug");
      setMessage(messages.liveAnalysis.redirecting.replace("{repo}", result.repo ?? trimmedRepo));
      router.push(workspaceHref(result.workspace_slug, result.job_id));
    } catch (error) {
      const detail = error instanceof Error ? error.message : "unknown error";
      setActionError(true);
      setMessage(messages.liveAnalysis.failed.replace("{detail}", detail));
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTouched(true);
    if (!canCreate) {
      if (existing) setMessage(messages.liveAnalysis.reuseDetected);
      return;
    }
    await startImport("full", null);
  }

  return (
    <form className="live-import-form" onSubmit={handleSubmit} aria-label={messages.liveAnalysis.importSectionLabel}>
      <div className="live-import-entry">
        <div className="field live-import-field">
          <label htmlFor="live-analysis-repo">{messages.liveAnalysis.label}</label>
          <input
            id="live-analysis-repo"
            type="text"
            inputMode="url"
            autoComplete="url"
            spellCheck={false}
            value={repo}
            onChange={(event) => {
              setRepo(event.target.value);
              setMessage(null);
              setActionError(false);
            }}
            onBlur={() => setTouched(true)}
            aria-invalid={showInvalidRepo}
            aria-describedby={showInvalidRepo ? "live-analysis-repo-help live-analysis-repo-error" : "live-analysis-repo-help"}
            placeholder={messages.liveAnalysis.placeholder}
          />
          <p className="muted live-import-help" id="live-analysis-repo-help">{messages.liveAnalysis.helper}</p>
          {showInvalidRepo ? (
            <p id="live-analysis-repo-error" className="form-feedback form-feedback-error" role="alert">
              {messages.liveAnalysis.invalidRepo}
            </p>
          ) : null}
        </div>
        <button className="action-link-primary live-import-submit" type="submit" disabled={!canCreate}>
          {loading ? messages.liveAnalysis.submittingButton : messages.liveAnalysis.submit}
        </button>
      </div>

      <div className="live-import-feedback" role="status" aria-live="polite" aria-atomic="true">
        {lookupLoading ? <p>{messages.liveAnalysis.lookupLoading}</p> : null}
        {lookupFailed ? (
          <div className="live-import-retry">
            <p className="form-feedback form-feedback-error">{messages.liveAnalysis.lookupFailed}</p>
            <button type="button" onClick={() => setRetryCount((value) => value + 1)}>
              {messages.liveAnalysis.retryLookup}
            </button>
          </div>
        ) : null}
        {lookup && !lookup.workspace_exists && !lookupAccessRequirement ? (
          <p className="form-feedback form-feedback-success">{messages.liveAnalysis.readyToImport}</p>
        ) : null}
        {!existing && lookupAccessRequirement ? (
          <p className="form-feedback form-feedback-error">{lookupAccessRequirement}</p>
        ) : null}
        {!existing && lookup?.access_requirement_detail ? (
          <p className="form-feedback form-feedback-error">{lookup.access_requirement_detail}</p>
        ) : null}
        {message ? <p className={actionError ? "form-feedback form-feedback-error" : "form-feedback"}>{message}</p> : null}
      </div>

      {lookup?.workspace_exists && lookup.workspace_slug ? (
        <section className="live-import-existing" aria-labelledby="live-import-existing-title">
          <div className="live-import-existing-header">
            <div>
              <p className="eyebrow">{messages.liveAnalysis.importSectionLabel}</p>
              <h3 id="live-import-existing-title">{messages.liveAnalysis.reuseTitle}</h3>
            </div>
            <span className="live-import-existing-indicator" aria-hidden="true" />
          </div>
          <p>{messages.liveAnalysis.reuseBody.replace("{workspace}", lookup.workspace_slug)}</p>
          {lookup.access_source_label ? <p className="muted">{messages.liveAnalysis.accessSource.replace("{source}", lookup.access_source_label)}</p> : null}
          {lookupAccessStatus ? <p className="muted">{messages.liveAnalysis.accessSourceStatus.replace("{status}", lookupAccessStatus)}</p> : null}
          {lookup.access_source_status_detail ? (
            <p className="muted">{messages.liveAnalysis.accessSourceDetail.replace("{detail}", lookup.access_source_status_detail)}</p>
          ) : null}
          {latestLookupSyncSummary ? (
            <p className="muted">{messages.liveAnalysis.latestSync.replace("{summary}", latestLookupSyncSummary)}</p>
          ) : null}
          {lookup.has_running_import ? <p className="form-feedback">{messages.liveAnalysis.runningImportHint}</p> : null}
          <div className="action-row live-import-existing-actions">
            <Link
              href={workspaceHref(
                lookup.workspace_slug,
                lookup.has_running_import ? lookup.active_import?.job_id ?? lookup.latest_import?.job_id : null
              )}
              className="action-link action-link-primary"
            >
              {messages.liveAnalysis.openExisting}
            </Link>
            <button
              type="button"
              disabled={loading || lookupLoading || !lookup.can_incremental_sync || lookup.has_running_import}
              onClick={() => startImport("since_last_sync", lookup.workspace_slug)}
            >
              {messages.liveAnalysis.syncExisting}
            </button>
            <button
              type="button"
              disabled={loading || lookupLoading || lookup.has_running_import}
              onClick={() => startImport("full", lookup.workspace_slug)}
            >
              {messages.liveAnalysis.rerunFull}
            </button>
          </div>
        </section>
      ) : null}
    </form>
  );
}
