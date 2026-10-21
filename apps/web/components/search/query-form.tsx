"use client";

import Link from "next/link";
import React, { useRef, useState } from "react";

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
  const [validationError, setValidationError] = useState(false);
  const pendingRef = useRef(false);
  const requestVersion = useRef(0);
  const trimmedQuestion = question.trim();

  function updateQuestion(nextQuestion: string) {
    setQuestion(nextQuestion);
    setError(null);
    setValidationError(false);
    setResult(null);
    requestVersion.current += 1; // Never show an answer for an edited question.
  }
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
    const normalized = nextQuestion.trim();
    if (!normalized) {
      setValidationError(true);
      return;
    }
    if (pendingRef.current) return;
    pendingRef.current = true;
    const version = ++requestVersion.current;
    setLoading(true);
    setValidationError(false);
    setError(null);
    setResult(null);
    try {
      const response = await askWhy(workspaceSlug, normalized);
      if (version === requestVersion.current) setResult(response);
    } catch {
      if (version === requestVersion.current) setError(messages.search.error);
    } finally {
      pendingRef.current = false;
      setLoading(false);
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runQuestion(question);
  }

  return (
    <div className="stack">
      <section className="search-suggestions" aria-labelledby="why-search-examples-title">
        <h2 id="why-search-examples-title">{messages.search.examplesTitle}</h2>
        <p className="muted">{messages.search.exampleHint}</p>
        <div className="search-suggestion-list">
          {messages.search.examples.map((example) => (
            <button key={example} type="button" disabled={loading} onClick={() => updateQuestion(example)}>
              {example}
            </button>
          ))}
        </div>
      </section>
      {isGuidedDemoWorkspace ? (
        <div className="action-row">
          <button type="button" className="action-link action-link-primary" onClick={() => void runQuestion(question)} disabled={loading || !trimmedQuestion}>
            {messages.guidedDemo.searchRunExample}
          </button>
        </div>
      ) : null}
      <form className="search-form" onSubmit={handleSubmit} aria-busy={loading}>
        <label className="field">
          <span>{messages.search.askWhy}</span>
          <input
            value={question}
            onChange={(event) => updateQuestion(event.target.value)}
            placeholder={messages.search.placeholder}
            aria-invalid={validationError}
            aria-describedby={validationError ? "why-question-error" : undefined}
          />
        </label>
        <button type="submit" disabled={loading || !trimmedQuestion}>
          {loading ? messages.search.searching : messages.search}
        </button>
      </form>
      {validationError ? (
        <p id="why-question-error" className="form-feedback form-feedback-error" role="alert">
          {messages.search.questionRequired}
        </p>
      ) : null}
      {!result && !error ? <p>{isGuidedDemoWorkspace ? messages.search.intro : messages.search.importedIntro}</p> : null}
      <div aria-live="polite" role="status" className="search-request-status">
        {loading ? <p>{messages.search.searching}</p> : null}
        {error ? (
          <div className="search-retry">
            <p className="form-feedback form-feedback-error">{error}</p>
            <button type="button" onClick={() => void runQuestion(question)} disabled={loading || !trimmedQuestion}>
              {messages.search.retryQuestion}
            </button>
          </div>
        ) : null}
      </div>
      {result ? <SearchResults result={result} /> : null}
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
