"use client";

import React from "react";

import { DriftAlertsResponse } from "../../lib/api";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { useI18n } from "../i18n/language-provider";
import { AlertDetail } from "./alert-detail";
import { ProvenanceBanner } from "../provenance/provenance-banner";

export function DriftPageContent({
  drift,
  workspaceSlug,
}: {
  drift: DriftAlertsResponse | DriftAlertsResponse["alerts"];
  workspaceSlug: string;
}) {
  const { messages } = useI18n();
  const alerts = Array.isArray(drift) ? drift : drift.alerts;
  const provenance = Array.isArray(drift) ? null : drift;

  return (
    <main className="page-shell">
      <section className="panel stack">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/drift" />
        <div>
          <p className="eyebrow">{messages.drift.eyebrow}</p>
          <h1>{messages.drift.title}</h1>
          <p className="lede">{messages.drift.lede}</p>
        </div>
        {provenance ? (
          <ProvenanceBanner
            workspaceMode={provenance.workspace_mode}
            sourceSummary={provenance.source_summary}
            context="drift"
          />
        ) : null}
        {alerts.length === 0 ? (
          <p>{messages.drift.none}</p>
        ) : null}
        {alerts.map((alert) => (
          <AlertDetail key={alert.id} alert={alert} workspaceSlug={workspaceSlug} />
        ))}
      </section>
    </main>
  );
}
