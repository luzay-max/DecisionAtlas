"use client";

import Link from "next/link";
import React, { useState } from "react";

import { askWhy, WhyAnswerResponse } from "../../lib/api";
import { SearchResults } from "./search-results";
import { useI18n } from "../i18n/language-provider";

const nextActionHref: Record<string, (workspaceSlug: string) => string> = {
  review_candidates: (workspaceSlug) => `/review?workspace=${encodeURIComponent(workspaceSlug)}`,
  ask_why: (workspaceSlug) => `/search?workspace=${encodeURIComponent(workspaceSlug)}`,
  evaluate_drift: (workspaceSlug) => `/drift?workspace=${encodeURIComponent(workspaceSlug)}`,
  inspect_import_summary: (workspaceSlug) => `/workspaces/${encodeURIComponent(workspaceSlug)}`,
  retry_import: (workspaceSlug) => `/workspaces/${encodeURIComponent(workspaceSlug)}`,
  inspect_alerts: (workspaceSlug) => `/drift?workspace=${encodeURIComponent(workspaceSlug)}`,
};

export function QueryForm({
  workspaceSlug,
  initialQuestion = "why use redis cache",
}: {
  workspaceSlug: string;
  initialQuestion?: string;
}) {
  const { messages } = useI18n();
  const [question, setQuestion] = useState(initialQuestion);
  const [result, setResult] = useState<WhyAnswerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isGuidedDemoWorkspace = workspaceSlug === "demo-workspace";
  const importedNextAction = !isGuidedDemoWorkspace ? result?.answer_context?.workspace_readiness?.next_action : null;
  const importedNextActionHref = importedNextAction ? nextActionHref[importedNextAction] : null;
  const renderedNextActionHref = isGuidedDemoWorkspace
    ? `/timeline?workspace=${encodeURIComponent(workspaceSlug)}`
    : importedNextActionHref?.(workspaceSlug);
  const nextActionLabel = isGuidedDemoWorkspace
    ? messages.guidedDemo.searchNext
    : importedNextAction
      ? messages.importedReadiness.actions[importedNextAction as keyof typeof messages.importedReadiness.actions] ??
        importedNextAction
      : null;

  async function runQuestion(nextQuestion: string) {
    setLoading(true);
    setError(null);
    try {
      const response = await askWhy(workspaceSlug, nextQuestion);
      setResult(response);
    } catch {
      setResult(null);
      setError(messages.search.error);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runQuestion(question);
  }

  return (
    <div className="stack">
      {isGuidedDemoWorkspace ? (
        <div className="action-row">
          <button type="button" className="action-link action-link-primary" onClick={() => void runQuestion(question)} disabled={loading}>
            {messages.guidedDemo.searchRunExample}
          </button>
        </div>
      ) : null}
      <form className="search-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>{messages.search.askWhy}</span>
          <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={messages.search.placeholder} />
        </label>
        <button type="submit">{loading ? messages.search.searching : messages.search.search}</button>
      </form>
      {!result && !error ? <p>{isGuidedDemoWorkspace ? messages.search.intro : messages.search.importedIntro}</p> : null}
      {error ? <p>{error}</p> : null}
      {result ? <SearchResults result={result} workspaceSlug={workspaceSlug} /> : null}
      {result && renderedNextActionHref && nextActionLabel ? (
        <div className="action-row">
          <Link href={renderedNextActionHref} className="action-link action-link-primary">
            {nextActionLabel}
          </Link>
        </div>
      ) : null}
    </div>
  );
}
