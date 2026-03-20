"use client";

import React from "react";

import { useI18n } from "../i18n/language-provider";

export function ReviewActions({ decisionId }: { decisionId: number }) {
  const { messages } = useI18n();

  return (
    <div className="action-row" aria-label={messages.review.actionsLabel.replace("{id}", String(decisionId))}>
      <button type="button">{messages.review.actions.accept}</button>
      <button type="button">{messages.review.actions.reject}</button>
      <button type="button">{messages.review.actions.supersede}</button>
    </div>
  );
}
