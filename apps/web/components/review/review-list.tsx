"use client";

import Link from "next/link";
import React, { useState } from "react";

import { reviewDecision, ReviewDecision, ReviewState } from "../../lib/api";
import { GuidedDemoPanel } from "../guided-demo/guided-demo-panel";
import { useI18n } from "../i18n/language-provider";
import { ReviewActions } from "./review-actions";
import { EvidenceReviewPanel } from "../evidence/evidence-review-panel";

function confidenceLabel(confidence: number, messages: ReturnType<typeof useI18n>["messages"]) {
  if (confidence >= 0.8) {
    return messages.review.confidenceHigh;
  }
  if (confidence >= 0.6) {
    return messages.review.confidenceMedium;
  }
  return messages.review.confidenceLow;
}

function qualityLabel(label: string | undefined, messages: ReturnType<typeof useI18n>["messages"]) {
  if (label === "strong") {
    return messages.review.qualityStrong;
  }
  if (label === "partial") {
    return messages.review.qualityPartial;
  }
  return messages.review.qualityThin;
}

function qualityReasonLabel(reason: string, messages: ReturnType<typeof useI18n>["messages"]) {
  return messages.review.qualityReasons[reason as keyof typeof messages.review.qualityReasons] ?? reason.replaceAll("_", " ");
}

export function ReviewList({ decisions, workspaceSlug }: { decisions: ReviewDecision[]; workspaceSlug: string }) {
  const { messages } = useI18n();
  const [items, setItems] = useState(decisions);
  const [acceptedInThisSession, setAcceptedInThisSession] = useState(0);
  const [query, setQuery] = useState("");
  const [evidenceFilter, setEvidenceFilter] = useState<"all" | "strong" | "partial" | "thin">("all");
  const normalizedQuery = query.trim().toLocaleLowerCase();
  const filteredItems = items.filter((decision) => {
    const quality = decision.candidate_quality?.label ?? "thin";
    const matchesEvidence = evidenceFilter === "all" || quality === evidenceFilter;
    const matchesQuery = !normalizedQuery ||
      [decision.title, decision.problem, decision.chosen_option]
        .some((value) => (value ?? "").toLocaleLowerCase().includes(normalizedQuery));
    return matchesEvidence && matchesQuery;
  });
  const startedWithItems = decisions.length > 0;
  const isGuidedDemoWorkspace = workspaceSlug === "demo-workspace";
  const isImportedWorkspace = !isGuidedDemoWorkspace;

  async function handleReview(decisionId: number, reviewState: ReviewState) {
    await reviewDecision(decisionId, reviewState);
    if (reviewState === "accepted") setAcceptedInThisSession((count) => count + 1);
    setItems((current) => current.filter((decision) => decision.id !== decisionId));
  }

  return (
    <div className="stack">
      {items.length > 0 ? (
        <section className="review-queue-controls" aria-label={messages.review.filterLabel}>
          <div className="review-queue-heading">
            <h2>{messages.review.queueCount.replace("{count}", String(items.length))}</h2>
            <span className="badge" role="status" aria-live="polite">
              {messages.review.remainingCount.replace("{count}", String(filteredItems.length))}
            </span>
          </div>
          <div className="review-queue-fields">
            <label className="field">
              <span>{messages.review.searchCandidates}</span>
              <input
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder={messages.review.searchPlaceholder}
              />
            </label>
            <label className="field">
              <span>{messages.review.filterLabel}</span>
              <select
                value={evidenceFilter}
                onChange={(event) => setEvidenceFilter(event.target.value as typeof evidenceFilter)}
              >
                <option value="all">{messages.review.filterAll}</option>
                <option value="strong">{messages.review.filterStrong}</option>
                <option value="partial">{messages.review.filterPartial}</option>
                <option value="thin">{messages.review.filterThin}</option>
              </select>
            </label>
          </div>
          {filteredItems.length === 0 ? (
            <div className="review-empty-filter" role="status">
              <p>{messages.review.noFilterResults}</p>
              <button type="button" onClick={() => { setQuery(""); setEvidenceFilter("all"); }}>
                {messages.review.clearFilters}
              </button>
            </div>
          ) : null}
        </section>
      ) : null}
      {items.length === 0 ? (
        startedWithItems && acceptedInThisSession > 0 && isGuidedDemoWorkspace ? (
          <GuidedDemoPanel
            step={2}
            total={messages.guidedDemo.steps.length}
            title={messages.review.completed}
            description={messages.guidedDemo.reviewDescription}
            steps={messages.guidedDemo.steps}
            status={messages.guidedDemo.reviewCompletedStatus}
            nextHref={`/search?workspace=${encodeURIComponent(workspaceSlug)}`}
            nextLabel={messages.guidedDemo.reviewNext}
            tone="success"
          />
        ) : startedWithItems && acceptedInThisSession > 0 && isImportedWorkspace ? (
          <div className="card">
            <p className="eyebrow">{messages.review.importedBaselineTitle}</p>
            <p>{messages.review.importedBaselineStatus}</p>
            <div className="action-row">
              <Link href={`/search?workspace=${encodeURIComponent(workspaceSlug)}`} className="action-link action-link-primary">
                {messages.review.importedBaselineNext}
              </Link>
              <Link href={`/drift?workspace=${encodeURIComponent(workspaceSlug)}`} className="action-link">
                {messages.review.importedDriftNext}
              </Link>
            </div>
          </div>
        ) : startedWithItems ? (
          <div className="card">
            <p className="eyebrow">{messages.review.reviewedWithoutAcceptanceTitle}</p>
            <p>{messages.review.reviewedWithoutAcceptanceStatus}</p>
            <Link href={`/workspaces/${encodeURIComponent(workspaceSlug)}`} className="action-link">
              {messages.review.reviewedWithoutAcceptanceNext}
            </Link>
          </div>
        ) : (
          <p>{isGuidedDemoWorkspace ? messages.review.emptyDemo : messages.review.emptyImported}</p>
        )
      ) : null}
      {filteredItems.map((decision) => {
        const evidence = decision.review_evidence;
        const quality = decision.candidate_quality;
        const evidenceState = evidence?.state ?? "missing";
        const evidenceLabel =
          evidenceState === "grounded"
            ? messages.review.evidenceGrounded
            : evidenceState === "thin"
              ? messages.review.evidenceThin
              : messages.review.evidenceMissing;
        const detailHref = `/decisions/${decision.id}?workspace=${encodeURIComponent(workspaceSlug)}`;

        return (
          <article key={decision.id} className="card">
            <div className="card-head">
              <div>
                <p className="eyebrow">{messages.review.candidateDecision}</p>
                <h2>
                  <Link href={detailHref} className="title-link">
                    {decision.title}
                  </Link>
                </h2>
              </div>
              <span className="badge">
                {messages.status[decision.review_state as keyof typeof messages.status] ?? decision.review_state}
              </span>
            </div>
            <p>
              <strong>{messages.review.confidence}:</strong> {decision.confidence.toFixed(2)} ·{" "}
              {confidenceLabel(decision.confidence, messages)}
            </p>
            {isImportedWorkspace ? (
              <div className="callout">
                <p className="eyebrow">{messages.review.evidence}</p>
                <p>
                  <span className="badge">{qualityLabel(quality?.label, messages)}</span>{" "}
                  {quality?.summary ?? messages.review.qualityThinSummary}
                </p>
                <p>
                  <strong>{evidenceLabel}</strong>
                  {evidence ? ` · ${messages.review.sourceRefs.replace("{count}", String(evidence.source_ref_count))}` : null}
                  {quality
                    ? ` · ${messages.review.previewableSourceRefs.replace("{count}", String(quality.previewable_source_ref_count))}`
                    : null}
                </p>
                {quality?.reasons?.length ? (
                  <p className="muted">
                    <strong>{messages.review.qualityReasonsTitle}:</strong>{" "}
                    {quality.reasons.map((reason) => qualityReasonLabel(reason, messages)).join(" · ")}
                  </p>
                ) : null}
                {quality?.label === "partial" ? <p className="muted">{messages.review.qualityPartialGuidance}</p> : null}
                {quality?.label === "thin" ? <p className="muted">{messages.review.qualityThinGuidance}</p> : null}
                {evidence?.primary_artifact ? (
                  <p>
                    <strong>{messages.review.sourceArtifact}:</strong>{" "}
                    {evidence.primary_artifact.url ? (
                      <a href={evidence.primary_artifact.url}>
                        {evidence.primary_artifact.title ?? `Artifact ${evidence.primary_artifact.id}`}
                      </a>
                    ) : (
                      evidence.primary_artifact.title ?? `Artifact ${evidence.primary_artifact.id}`
                    )}{" "}
                    <span className="muted">
                      ({messages.review.sourceType}: {evidence.primary_artifact.type}
                      {evidence.primary_artifact.repo ? ` · ${evidence.primary_artifact.repo}` : ""})
                    </span>
                  </p>
                ) : null}
                {evidence?.source_ref_preview?.map((sourceRef) => (
                  <blockquote key={sourceRef.id}>
                    <strong>{messages.review.sourceQuote}:</strong> {sourceRef.quote}
                  </blockquote>
                ))}
                <EvidenceReviewPanel
                  sourceRefs={evidence?.source_ref_preview ?? []}
                  totalSourceCount={evidence?.source_ref_count ?? 0}
                  compact
                />
                <Link href={detailHref} className="action-link">
                  {messages.review.openDetail}
                </Link>
              </div>
            ) : null}
            <p>
              <strong>{messages.review.problem}:</strong> {decision.problem}
            </p>
            <p>
              <strong>{messages.review.chosenOption}:</strong> {decision.chosen_option}
            </p>
            <p>
              <strong>{messages.review.tradeoffs}:</strong> {decision.tradeoffs}
            </p>
            <ReviewActions decisionId={decision.id} onReview={(reviewState) => handleReview(decision.id, reviewState)} />
          </article>
        );
      })}
    </div>
  );
}
