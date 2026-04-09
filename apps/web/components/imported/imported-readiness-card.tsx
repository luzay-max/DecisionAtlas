"use client";

import Link from "next/link";
import React from "react";

import { WorkspaceReadiness } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

const actionHref: Record<string, (workspaceSlug: string) => string> = {
  review_candidates: (workspaceSlug) => `/review?workspace=${encodeURIComponent(workspaceSlug)}`,
  ask_why: (workspaceSlug) => `/search?workspace=${encodeURIComponent(workspaceSlug)}`,
  evaluate_drift: (workspaceSlug) => `/drift?workspace=${encodeURIComponent(workspaceSlug)}`,
  inspect_import_summary: (workspaceSlug) => `/workspaces/${encodeURIComponent(workspaceSlug)}`,
  retry_import: (workspaceSlug) => `/workspaces/${encodeURIComponent(workspaceSlug)}`,
  inspect_alerts: (workspaceSlug) => `/drift?workspace=${encodeURIComponent(workspaceSlug)}`,
};

export function ImportedReadinessCard({
  readiness,
  workspaceSlug,
}: {
  readiness: WorkspaceReadiness;
  workspaceSlug: string;
}) {
  const { messages } = useI18n();
  const title = messages.importedReadiness.states[readiness.state as keyof typeof messages.importedReadiness.states] ?? readiness.state;
  const detail =
    messages.importedReadiness.details[readiness.state as keyof typeof messages.importedReadiness.details] ?? readiness.state;
  const primaryActionLabel =
    messages.importedReadiness.actions[readiness.next_action as keyof typeof messages.importedReadiness.actions] ??
    readiness.next_action;
  const primaryHrefBuilder = actionHref[readiness.next_action];
  const recommendedActions = readiness.recommended_actions.filter((action) => action !== readiness.next_action);
  const reviewLabel =
    messages.importedReadiness.reviewStates[
      readiness.review_state as keyof typeof messages.importedReadiness.reviewStates
    ] ?? readiness.review_state;
  const whyLabel = messages.status[readiness.why_state as keyof typeof messages.status] ?? readiness.why_state;
  const driftLabel = messages.status[readiness.drift_state as keyof typeof messages.status] ?? readiness.drift_state;

  return (
    <section className="card stack">
      <p className="eyebrow">{messages.importedReadiness.eyebrow}</p>
      <h2>{title}</h2>
      <p>{detail}</p>
      <div className="stack">
        <p>
          <strong>{messages.importedReadiness.axes.review}:</strong> {reviewLabel}
        </p>
        <p>
          <strong>{messages.importedReadiness.axes.why}:</strong> {whyLabel}
        </p>
        <p>
          <strong>{messages.importedReadiness.axes.drift}:</strong> {driftLabel}
        </p>
      </div>
      {primaryHrefBuilder ? (
        <div className="action-row">
          <Link href={primaryHrefBuilder(workspaceSlug)} className="action-link action-link-primary">
            {primaryActionLabel}
          </Link>
          {recommendedActions.map((action) => {
            const hrefBuilder = actionHref[action];
            if (!hrefBuilder) {
              return null;
            }
            const label =
              messages.importedReadiness.actions[action as keyof typeof messages.importedReadiness.actions] ?? action;
            return (
              <Link key={action} href={hrefBuilder(workspaceSlug)} className="action-link">
                {label}
              </Link>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}
