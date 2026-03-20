"use client";

import React from "react";

import { DecisionDetail } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function DecisionCard({ decision }: { decision: DecisionDetail }) {
  const { messages } = useI18n();
  const reviewState = messages.status[decision.review_state as keyof typeof messages.status] ?? decision.review_state;

  return (
    <article className="card">
      <div className="card-head">
        <div>
          <p className="eyebrow">{messages.detail.eyebrow}</p>
          <h1>{decision.title}</h1>
        </div>
        <span className="badge">{reviewState}</span>
      </div>
      <p>
        <strong>{messages.detail.problem}:</strong> {decision.problem}
      </p>
      <p>
        <strong>{messages.detail.context}:</strong> {decision.context ?? messages.detail.na}
      </p>
      <p>
        <strong>{messages.detail.constraints}:</strong> {decision.constraints ?? messages.detail.na}
      </p>
      <p>
        <strong>{messages.detail.chosenOption}:</strong> {decision.chosen_option}
      </p>
      <p>
        <strong>{messages.detail.tradeoffs}:</strong> {decision.tradeoffs}
      </p>
      <p>
        <strong>{messages.detail.confidence}:</strong> {decision.confidence}
      </p>
    </article>
  );
}
