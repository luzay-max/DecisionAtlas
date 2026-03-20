"use client";

import React from "react";

import { DashboardSummary } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function KpiStrip({ summary }: { summary: DashboardSummary }) {
  const { messages } = useI18n();
  const importStatus = messages.status[summary.import_status as keyof typeof messages.status] ?? summary.import_status;

  return (
    <div className="kpi-strip">
      <article className="card">
        <p className="eyebrow">{messages.kpi.importStatus}</p>
        <p>{importStatus}</p>
      </article>
      <article className="card">
        <p className="eyebrow">{messages.kpi.artifacts}</p>
        <p>{summary.artifact_count}</p>
      </article>
      <article className="card">
        <p className="eyebrow">{messages.kpi.acceptedDecisions}</p>
        <p>{summary.decision_counts.accepted}</p>
      </article>
      <article className="card">
        <p className="eyebrow">{messages.kpi.candidateDecisions}</p>
        <p>{summary.decision_counts.candidate}</p>
      </article>
    </div>
  );
}
