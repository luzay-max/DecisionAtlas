"use client";

import Link from "next/link";
import React from "react";

import { DashboardSummary } from "../../lib/api";
import { DemoImportButton } from "./demo-import-button";
import { KpiStrip } from "./kpi-strip";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { RecentAlerts } from "./recent-alerts";
import { useI18n } from "../i18n/language-provider";
import { ProvenanceBanner } from "../provenance/provenance-banner";

export function WorkspaceDashboardContent({ summary }: { summary: DashboardSummary }) {
  const { messages } = useI18n();
  const latestImportStatus = summary.latest_import
    ? (messages.status[summary.latest_import.status as keyof typeof messages.status] ?? summary.latest_import.status)
    : null;
  const latestImportMode = summary.latest_import
    ? (messages.dashboard.importMode[summary.latest_import.mode as keyof typeof messages.dashboard.importMode] ??
      summary.latest_import.mode)
    : null;

  return (
    <main className="page-shell">
      <section className="panel stack">
        <DemoWorkspaceNav workspaceSlug={summary.workspace_slug} currentPath={`/workspaces/${summary.workspace_slug}`} />
        <div>
          <p className="eyebrow">{messages.dashboard.eyebrow}</p>
          <h1>{summary.workspace_slug}</h1>
          <p>
            {messages.dashboard.demoRepo}: {summary.github_repo}
          </p>
        </div>
        <ProvenanceBanner
          workspaceMode={summary.workspace_mode}
          sourceSummary={summary.source_summary}
          context="dashboard"
        />
        <DemoImportButton workspaceSlug={summary.workspace_slug} repo={summary.github_repo} />
        <div className="action-row">
          <Link href={`/review?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            {messages.dashboard.reviewCandidates}
          </Link>
          <Link href={`/search?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            {messages.dashboard.askWhy}
          </Link>
          <Link href={`/drift?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            {messages.dashboard.inspectDrift}
          </Link>
          <Link href={`/timeline?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            {messages.dashboard.openTimeline}
          </Link>
        </div>
        {summary.latest_import ? (
          <div className="stack">
            <p className="eyebrow">{messages.dashboard.latestImport}</p>
            <p>
              {latestImportStatus} · {latestImportMode} · {summary.latest_import.imported_count}{" "}
              {messages.kpi.artifacts}
            </p>
            {summary.latest_import.error_message ? <p>{summary.latest_import.error_message}</p> : null}
          </div>
        ) : null}
        <KpiStrip summary={summary} />
        <RecentAlerts summary={summary} />
      </section>
    </main>
  );
}
