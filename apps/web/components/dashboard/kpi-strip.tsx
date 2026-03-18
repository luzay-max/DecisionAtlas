import React from "react";

import { DashboardSummary } from "../../lib/api";

export function KpiStrip({ summary }: { summary: DashboardSummary }) {
  return (
    <div className="kpi-strip">
      <article className="card">
        <p className="eyebrow">Import Status</p>
        <p>{summary.import_status}</p>
      </article>
      <article className="card">
        <p className="eyebrow">Artifacts</p>
        <p>{summary.artifact_count}</p>
      </article>
      <article className="card">
        <p className="eyebrow">Accepted Decisions</p>
        <p>{summary.decision_counts.accepted}</p>
      </article>
      <article className="card">
        <p className="eyebrow">Candidate Decisions</p>
        <p>{summary.decision_counts.candidate}</p>
      </article>
    </div>
  );
}
