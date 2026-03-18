import React from "react";

import { DashboardSummary } from "../../lib/api";

export function RecentAlerts({ summary }: { summary: DashboardSummary }) {
  return (
    <section className="stack">
      <h2>Recent Alerts</h2>
      {summary.recent_alerts.length === 0 ? <p>No alerts yet.</p> : null}
      {summary.recent_alerts.map((alert) => (
        <article key={alert.id} className="card">
          <div className="card-head">
            <strong>{alert.alert_type}</strong>
            <span className="badge">{alert.status}</span>
          </div>
          <p>{alert.summary}</p>
        </article>
      ))}
    </section>
  );
}
