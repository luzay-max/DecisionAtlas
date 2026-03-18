import Link from "next/link";
import React from "react";

import { DashboardSummary } from "../../lib/api";
import { DemoImportButton } from "./demo-import-button";
import { KpiStrip } from "./kpi-strip";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { RecentAlerts } from "./recent-alerts";

export function WorkspaceDashboardContent({ summary }: { summary: DashboardSummary }) {
  return (
    <main className="page-shell">
      <section className="panel stack">
        <DemoWorkspaceNav workspaceSlug={summary.workspace_slug} currentPath={`/workspaces/${summary.workspace_slug}`} />
        <div>
          <p className="eyebrow">Workspace Dashboard</p>
          <h1>{summary.workspace_slug}</h1>
          <p>Demo repo: {summary.github_repo}</p>
        </div>
        <DemoImportButton workspaceSlug={summary.workspace_slug} repo={summary.github_repo} />
        <div className="action-row">
          <Link href={`/review?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            Review candidates
          </Link>
          <Link href={`/search?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            Ask why
          </Link>
          <Link href={`/drift?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            Inspect drift
          </Link>
          <Link href={`/timeline?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            Open timeline
          </Link>
        </div>
        {summary.latest_import ? (
          <div className="stack">
            <p className="eyebrow">Latest Import</p>
            <p>
              {summary.latest_import.status} via {summary.latest_import.mode} mode,{" "}
              {summary.latest_import.imported_count} artifacts
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
