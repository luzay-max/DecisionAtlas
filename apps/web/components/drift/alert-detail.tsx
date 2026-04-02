"use client";

import Link from "next/link";
import React from "react";

import { DriftAlertItem } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function AlertDetail({ alert, workspaceSlug }: { alert: DriftAlertItem; workspaceSlug: string }) {
  const { messages } = useI18n();
  const confidence = messages.status[alert.confidence_label as keyof typeof messages.status] ?? alert.confidence_label;
  const alertStatus = messages.status[alert.status as keyof typeof messages.status] ?? alert.status;
  const alertType = messages.status[alert.alert_type as keyof typeof messages.status] ?? alert.alert_type;
  const alertTypeDetail =
    messages.drift.alertTypeDetails?.[alert.alert_type as keyof typeof messages.drift.alertTypeDetails] ?? null;
  const groupedFollowup =
    alert.alert_type === "needs_review" && /related follow-up artifact/i.test(alert.summary);

  return (
    <article className="card stack">
      <div className="card-head">
        <div>
          <strong>{alertType}</strong>
          {alertTypeDetail ? <p>{alertTypeDetail}</p> : null}
          {groupedFollowup ? <p>{messages.drift.groupedFollowupHint}</p> : null}
          <p>{alert.summary}</p>
        </div>
        <div className="stack">
          <span className="badge">{alertStatus}</span>
          <span className="badge">
            {confidence} {messages.drift.confidence}
          </span>
        </div>
      </div>
      {alert.decision ? (
        <div className="stack">
          <p>
            {messages.drift.matchedDecision}:{" "}
            <strong>
              <Link
                href={`/decisions/${alert.decision.id}?workspace=${encodeURIComponent(workspaceSlug)}`}
                className="title-link"
              >
                {alert.decision.title}
              </Link>
            </strong>
          </p>
          <p>
            {messages.review.chosenOption}: {alert.decision.chosen_option}
          </p>
        </div>
      ) : null}
      {alert.artifact ? (
        <p>
          {messages.drift.triggeringArtifact}:{" "}
          {alert.artifact.url ? (
            <a href={alert.artifact.url}>{alert.artifact.title ?? `Artifact ${alert.artifact.id}`}</a>
          ) : (
            <strong>{alert.artifact.title ?? `Artifact ${alert.artifact.id}`}</strong>
          )}
        </p>
      ) : null}
    </article>
  );
}
