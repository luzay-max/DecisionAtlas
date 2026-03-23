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
  const actionLabel =
    messages.importedReadiness.actions[readiness.next_action as keyof typeof messages.importedReadiness.actions] ??
    readiness.next_action;
  const hrefBuilder = actionHref[readiness.next_action];

  return (
    <section className="card stack">
      <p className="eyebrow">{messages.importedReadiness.eyebrow}</p>
      <h2>{title}</h2>
      <p>{detail}</p>
      {hrefBuilder ? (
        <div className="action-row">
          <Link href={hrefBuilder(workspaceSlug)} className="action-link action-link-primary">
            {actionLabel}
          </Link>
        </div>
      ) : null}
    </section>
  );
}
