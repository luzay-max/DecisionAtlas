import React from "react";

import { KpiStrip } from "../../../components/dashboard/kpi-strip";
import { RecentAlerts } from "../../../components/dashboard/recent-alerts";
import { DashboardSummary, getDashboardSummary } from "../../../lib/api";

export function WorkspaceDashboardContent({ summary }: { summary: DashboardSummary }) {
  return (
    <main className="page-shell">
      <section className="panel stack">
        <div>
          <p className="eyebrow">Workspace Dashboard</p>
          <h1>{summary.workspace_slug}</h1>
        </div>
        <KpiStrip summary={summary} />
        <RecentAlerts summary={summary} />
      </section>
    </main>
  );
}

export default async function WorkspaceDashboardPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const summary = await getDashboardSummary(slug);
  return <WorkspaceDashboardContent summary={summary} />;
}
