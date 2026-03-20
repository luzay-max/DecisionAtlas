"use client";

import Link from "next/link";
import React, { useState } from "react";

import { reviewDecision, ReviewDecision, ReviewState } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";
import { ReviewActions } from "./review-actions";

export function ReviewList({ decisions, workspaceSlug }: { decisions: ReviewDecision[]; workspaceSlug: string }) {
  const { messages } = useI18n();
  const [items, setItems] = useState(decisions);

  async function handleReview(decisionId: number, reviewState: ReviewState) {
    await reviewDecision(decisionId, reviewState);
    setItems((current) => current.filter((decision) => decision.id !== decisionId));
  }

  return (
    <div className="stack">
      {items.length === 0 ? (
        <p>{workspaceSlug === "demo-workspace" ? messages.review.emptyDemo : messages.review.emptyImported}</p>
      ) : null}
      {items.map((decision) => (
        <article key={decision.id} className="card">
          <div className="card-head">
            <div>
              <p className="eyebrow">{messages.review.candidateDecision}</p>
              <h2>
                <Link
                  href={`/decisions/${decision.id}?workspace=${encodeURIComponent(workspaceSlug)}`}
                  className="title-link"
                >
                  {decision.title}
                </Link>
              </h2>
            </div>
            <span className="badge">{messages.status[decision.review_state as keyof typeof messages.status] ?? decision.review_state}</span>
          </div>
          <p>
            <strong>{messages.review.confidence}:</strong> {decision.confidence.toFixed(2)}
          </p>
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
      ))}
    </div>
  );
}
