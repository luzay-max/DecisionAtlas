import React from "react";

import { WorkspaceDashboardContent } from "../../../components/dashboard/workspace-dashboard-content";
import { getDashboardSummary } from "../../../lib/api";

export default async function WorkspaceDashboardPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  try {
    const summary = await getDashboardSummary(slug);
    return <WorkspaceDashboardContent summary={summary} />;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load dashboard summary";
    return (
      <main className="page-shell">
        <section className="panel stack">
          <p className="eyebrow">Workspace dashboard</p>
          <h1>{slug}</h1>
          <p>Dashboard summary is temporarily unavailable.</p>
          <p>{message}</p>
        </section>
      </main>
    );
  }
}
