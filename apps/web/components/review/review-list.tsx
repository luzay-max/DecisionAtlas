"use client";

import Link from "next/link";
import React, { useState } from "react";

import { reviewDecision, ReviewDecision, ReviewState } from "../../lib/api";
import { GuidedDemoPanel } from "../guided-demo/guided-demo-panel";
import { useI18n } from "../i18n/language-provider";
import { ReviewActions } from "./review-actions";

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

export function ReviewList({ decisions, workspaceSlug }: { decisions: ReviewDecision[]; workspaceSlug: string }) {
  const { messages } = useI18n();
  const [items, setItems] = useState(decisions);
  const startedWithItems = decisions.length > 0;
  const isGuidedDemoWorkspace = workspaceSlug === "demo-workspace";
  const isImportedWorkspace = !isGuidedDemoWorkspace;

  async function handleReview(decisionId: number, reviewState: ReviewState) {
    await reviewDecision(decisionId, reviewState);
    setItems((current) => current.filter((decision) => decision.id !== decisionId));
  }

  return (
    <div className="stack">
      {items.length === 0 ? (
        isGuidedDemoWorkspace && startedWithItems ? (
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
        ) : isImportedWorkspace && startedWithItems ? (
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
        ) : (
          <p>{workspaceSlug === "demo-workspace" ? messages.review.emptyDemo : messages.review.emptyImported}</p>
        )
      ) : null}
      {items.map((decision) => {
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
