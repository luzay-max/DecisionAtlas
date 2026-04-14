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
  const latestSyncOrigin = readiness.latest_sync_origin
    ? messages.status[readiness.latest_sync_origin as keyof typeof messages.status] ?? readiness.latest_sync_origin
    : null;
  const activeSyncOrigin = readiness.active_sync_origin
    ? messages.status[readiness.active_sync_origin as keyof typeof messages.status] ?? readiness.active_sync_origin
    : null;
  const syncEventLabel = (event: string | null | undefined) =>
    event ? messages.syncEvents[event as keyof typeof messages.syncEvents] ?? event : null;

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
        {readiness.access_source_label ? (
          <p>
            <strong>{messages.importedReadiness.axes.source}:</strong> {readiness.access_source_label}
          </p>
        ) : null}
        {readiness.access_source_status ? (
          <p>
            <strong>{messages.importedReadiness.axes.sourceStatus}:</strong>{" "}
            {messages.status[readiness.access_source_status as keyof typeof messages.status] ?? readiness.access_source_status}
          </p>
        ) : null}
        {readiness.access_source_status_detail ? <p>{readiness.access_source_status_detail}</p> : null}
        {latestSyncOrigin ? (
          <p>
            <strong>{messages.importedReadiness.axes.sync}:</strong> {latestSyncOrigin}
            {readiness.latest_sync_at ? ` · ${readiness.latest_sync_at}` : ""}
          </p>
        ) : null}
        {activeSyncOrigin ? (
          <p>
            <strong>{messages.importedReadiness.axes.activeSync}:</strong> {activeSyncOrigin}
          </p>
        ) : null}
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
      {readiness.recent_syncs && readiness.recent_syncs.length > 0 ? (
        <div className="stack">
          <p>
            <strong>{messages.importedReadiness.recentSyncs}</strong>
          </p>
          {readiness.recent_syncs.slice(0, 3).map((sync) => {
            const syncOrigin = sync.sync_origin
              ? messages.status[sync.sync_origin as keyof typeof messages.status] ?? sync.sync_origin
              : sync.mode;
            const syncStatus = messages.status[sync.status as keyof typeof messages.status] ?? sync.status;
            const triggerEvent = sync.trigger_event
              ? syncEventLabel(sync.trigger_event)
              : null;
            return (
              <p key={sync.job_id}>
                {syncOrigin} · {syncStatus}
                {triggerEvent ? ` · ${triggerEvent}` : ""}
              </p>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}
