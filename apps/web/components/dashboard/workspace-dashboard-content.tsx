import React from "react";

import { DashboardSummary } from "../../lib/api";
import { DemoImportButton } from "./demo-import-button";
import { KpiStrip } from "./kpi-strip";
import { RecentAlerts } from "./recent-alerts";

export function WorkspaceDashboardContent({ summary }: { summary: DashboardSummary }) {
  return (
    <main className="page-shell">
      <section className="panel stack">
        <div>
          <p className="eyebrow">Workspace Dashboard</p>
          <h1>{summary.workspace_slug}</h1>
        </div>
        <DemoImportButton workspaceSlug={summary.workspace_slug} />
        <KpiStrip summary={summary} />
        <RecentAlerts summary={summary} />
      </section>
    </main>
  );
}
