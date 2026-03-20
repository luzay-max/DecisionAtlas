"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

import { startGithubImport } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function LiveAnalysisForm() {
  const { messages } = useI18n();
  const router = useRouter();
  const [repo, setRepo] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage(messages.liveAnalysis.submitting);
    try {
      const result = await startGithubImport(null, repo);
      const workspaceSlug = result.workspace_slug;
      if (!workspaceSlug) {
        throw new Error("Missing workspace slug");
      }
      setMessage(messages.liveAnalysis.redirecting.replace("{repo}", result.repo ?? repo));
      router.push(`/workspaces/${encodeURIComponent(workspaceSlug)}`);
    } catch (error) {
      const detail = error instanceof Error ? error.message : "unknown error";
      setMessage(messages.liveAnalysis.failed.replace("{detail}", detail));
    } finally {
      setLoading(false);
    }
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
      <button type="submit" disabled={loading || repo.trim().length === 0}>
        {loading ? messages.liveAnalysis.submittingButton : messages.liveAnalysis.submit}
      </button>
      <p>{messages.liveAnalysis.helper}</p>
      {message ? <p>{message}</p> : null}
    </form>
  );
}
