"use client";

import React from "react";

import { DashboardSummary } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function RecentAlerts({ summary }: { summary: DashboardSummary }) {
  const { messages } = useI18n();
  return (
    <section className="stack">
      <h2>{messages.alerts.recent}</h2>
      {summary.recent_alerts.length === 0 ? <p>{messages.alerts.none}</p> : null}
      {summary.recent_alerts.map((alert) => (
        <article key={alert.id} className="card">
          <div className="card-head">
            <strong>{alert.alert_type}</strong>
            <span className="badge">{messages.status[alert.status as keyof typeof messages.status] ?? alert.status}</span>
          </div>
          <p>{alert.summary}</p>
        </article>
      ))}
    </section>
  );
}
