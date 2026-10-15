"use client";

import React from "react";

import { useProductSession } from "../auth/session-provider";
import { useI18n } from "../i18n/language-provider";
import { ReviewDecision } from "../../lib/api";

function roleLabel(role: string | null | undefined, fallback: string) {
  return role ? role : fallback;
}

export function ReviewAuditPanel({ decisions }: { decisions: ReviewDecision[] }) {
  const { messages } = useI18n();
  const { session, status, canReviewWorkspace } = useProductSession();
  const role = roleLabel(session?.role, messages.review.localOperatorRole);
  const pendingCount = decisions.filter((decision) => decision.review_state === "candidate").length;
  const recentDecisions = decisions.slice(0, 3);

  return (
    <section className="callout" aria-label={messages.review.auditPanelLabel}>
      <div className="card-head">
        <div>
          <p className="eyebrow">{messages.review.roleEyebrow}</p>
          <h2>{messages.review.roleTitle.replace("{role}", role)}</h2>
        </div>
        <span className="badge">{canReviewWorkspace ? messages.review.roleCanReview : messages.review.roleReadOnly}</span>
      </div>
      <p>
        {status === "loading"
          ? messages.review.roleChecking
          : canReviewWorkspace
            ? messages.review.roleCanReviewDetail.replace("{count}", String(pendingCount))
            : messages.review.roleReadOnlyDetail}
      </p>
      <div className="stack" aria-label={messages.review.auditTrailLabel}>
        <p className="eyebrow">{messages.review.auditTrailTitle}</p>
        {recentDecisions.length > 0 ? (
          <ul>
            {recentDecisions.map((decision) => (
              <li key={decision.id}>
                <strong>{messages.review.auditCandidateQueued}</strong>: {decision.title}{" "}
                <span className="muted">
                  ({messages.review.auditState}:{" "}
                  {messages.status[decision.review_state as keyof typeof messages.status] ?? decision.review_state})
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p>{messages.review.auditEmpty}</p>
        )}
      </div>
      <p className="muted">{canReviewWorkspace ? messages.review.nextActionReviewer : messages.review.nextActionViewer}</p>
    </section>
  );
}
