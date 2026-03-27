"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { lookupGithubImport, type ImportLookup, startGithubImport } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function LiveAnalysisForm() {
  const { messages } = useI18n();
  const router = useRouter();
  const [repo, setRepo] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [lookup, setLookup] = useState<ImportLookup | null>(null);
  const [lookupLoading, setLookupLoading] = useState(false);

  useEffect(() => {
    const trimmedRepo = repo.trim();
    if (trimmedRepo.length < 3) {
      setLookup(null);
      setLookupLoading(false);
      return;
    }

    let cancelled = false;
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
  }, [repo]);

  async function startImport(mode: "full" | "since_last_sync", workspaceSlug: string | null) {
    setLoading(true);
    setMessage(
      mode === "since_last_sync"
        ? messages.liveAnalysis.syncSubmitting
        : messages.liveAnalysis.submitting
    );
    try {
      const result = await startGithubImport(workspaceSlug, repo, mode);
      const nextWorkspaceSlug = result.workspace_slug;
      if (!nextWorkspaceSlug) {
        throw new Error("Missing workspace slug");
      }
      setMessage(messages.liveAnalysis.redirecting.replace("{repo}", result.repo ?? repo));
      router.push(`/workspaces/${encodeURIComponent(nextWorkspaceSlug)}`);
    } catch (error) {
      const detail = error instanceof Error ? error.message : "unknown error";
      setMessage(messages.liveAnalysis.failed.replace("{detail}", detail));
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (lookup?.workspace_exists && lookup.workspace_slug) {
      setMessage(messages.liveAnalysis.reuseDetected);
      return;
    }
    await startImport("full", null);
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <label htmlFor="live-analysis-repo">
        <strong>{messages.liveAnalysis.label}</strong>
      </label>
      <input
        id="live-analysis-repo"
        type="text"
        value={repo}
        onChange={(event) => setRepo(event.target.value)}
        placeholder={messages.liveAnalysis.placeholder}
      />
      <button type="submit" disabled={loading || lookupLoading || repo.trim().length === 0}>
        {loading ? messages.liveAnalysis.submittingButton : messages.liveAnalysis.submit}
      </button>
      <p>{messages.liveAnalysis.helper}</p>
      {lookupLoading ? <p>{messages.liveAnalysis.lookupLoading}</p> : null}
      {lookup?.workspace_exists && lookup.workspace_slug ? (
        <div className="stack" style={{ border: "1px solid currentColor", borderRadius: "1rem", padding: "1rem" }}>
          <p><strong>{messages.liveAnalysis.reuseTitle}</strong></p>
          <p>{messages.liveAnalysis.reuseBody.replace("{workspace}", lookup.workspace_slug)}</p>
          {lookup.has_running_import ? <p>{messages.liveAnalysis.runningImportHint}</p> : null}
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <Link href={`/workspaces/${encodeURIComponent(lookup.workspace_slug)}`}>{messages.liveAnalysis.openExisting}</Link>
            <button
              type="button"
              disabled={loading || !lookup.can_incremental_sync}
              onClick={() => startImport("since_last_sync", lookup.workspace_slug)}
            >
              {messages.liveAnalysis.syncExisting}
            </button>
            <button
              type="button"
              disabled={loading || lookup.has_running_import}
              onClick={() => startImport("full", lookup.workspace_slug)}
            >
              {messages.liveAnalysis.rerunFull}
            </button>
          </div>
        </div>
      ) : null}
      {message ? <p>{message}</p> : null}
    </form>
  );
}
