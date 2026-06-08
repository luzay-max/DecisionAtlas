"use client";

import Link from "next/link";
import React from "react";

import { DriftAlertItem } from "../../lib/api";
import { ReviewOnly } from "../auth/role-gate";
import { useI18n } from "../i18n/language-provider";

export function AlertDetail({
  alert,
  workspaceSlug,
  onDisposition,
}: {
  alert: DriftAlertItem;
  workspaceSlug: string;
  onDisposition?: (
    alertId: number,
    status: "open" | "acknowledged" | "resolved" | "false_positive",
    rationale?: string
  ) => Promise<void>;
}) {
  const { messages } = useI18n();
  const [rationale, setRationale] = React.useState("");
  const [updatingStatus, setUpdatingStatus] = React.useState<string | null>(null);
  const confidence = messages.status[alert.confidence_label as keyof typeof messages.status] ?? alert.confidence_label;
  const alertStatus = messages.status[alert.status as keyof typeof messages.status] ?? alert.status;
  const alertType = messages.status[alert.alert_type as keyof typeof messages.status] ?? alert.alert_type;
  const alertTypeDetail =
    messages.drift.alertTypeDetails?.[alert.alert_type as keyof typeof messages.drift.alertTypeDetails] ?? null;
  const groupedFollowup =
    alert.alert_type === "needs_review" && /related follow-up artifact/i.test(alert.summary);

  async function submitDisposition(status: "open" | "acknowledged" | "resolved" | "false_positive") {
    if (!onDisposition) {
      return;
    }
    setUpdatingStatus(status);
    try {
      await onDisposition(alert.id, status, rationale);
      setRationale("");
    } finally {
      setUpdatingStatus(null);
    }
  }

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
      {alert.handled_by || alert.handled_at || alert.disposition_rationale ? (
        <p>
          <strong>Disposition:</strong> {alert.handled_by ? `handled by ${alert.handled_by}` : alert.status}
          {alert.handled_at ? ` at ${alert.handled_at}` : ""}
          {alert.disposition_rationale ? ` - ${alert.disposition_rationale}` : ""}
        </p>
      ) : null}
      {alert.audit_history?.length ? (
        <section className="stack" aria-label="Drift alert audit history">
          <h3>Handling history</h3>
          {alert.audit_history.map((event) => (
            <p key={event.id}>
              <strong>{event.actor_username}</strong> {event.action.replaceAll("_", " ")}
              {event.rationale ? `: ${event.rationale}` : ""}{" "}
              {event.created_at ? <span className="muted">{event.created_at}</span> : null}
            </p>
          ))}
        </section>
      ) : null}
      {onDisposition ? (
        <ReviewOnly>
          <section className="stack" aria-label="Drift alert disposition controls">
            <label>
              <strong>Disposition rationale</strong>
              <textarea rows={3} value={rationale} onChange={(event) => setRationale(event.target.value)} />
            </label>
            <div className="action-row">
              <button
                type="button"
                disabled={Boolean(updatingStatus)}
                onClick={() => submitDisposition("acknowledged")}
              >
                {updatingStatus === "acknowledged" ? "Updating..." : "Acknowledge"}
              </button>
              <button type="button" disabled={Boolean(updatingStatus)} onClick={() => submitDisposition("resolved")}>
                {updatingStatus === "resolved" ? "Updating..." : "Resolve"}
              </button>
              <button
                type="button"
                disabled={Boolean(updatingStatus)}
                onClick={() => submitDisposition("false_positive")}
              >
                {updatingStatus === "false_positive" ? "Updating..." : "False positive"}
              </button>
            </div>
          </section>
        </ReviewOnly>
      ) : null}
    </article>
  );
}
