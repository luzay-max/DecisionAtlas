"use client";

import React from "react";

import { DriftAlertsResponse } from "../../lib/api";
import { GuidedDemoPanel } from "../guided-demo/guided-demo-panel";
import { DriftEvaluationCard } from "./drift-evaluation-card";
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
  const isGuidedDemoWorkspace = workspaceSlug === "demo-workspace";

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
        {isGuidedDemoWorkspace ? (
          <GuidedDemoPanel
            step={5}
            total={messages.guidedDemo.steps.length}
            title={messages.guidedDemo.driftTitle}
            description={messages.guidedDemo.driftDescription}
            steps={messages.guidedDemo.steps}
            status={messages.guidedDemo.driftCompletedStatus}
            nextHref={`/workspaces/${encodeURIComponent(workspaceSlug)}`}
            nextLabel={messages.guidedDemo.driftNext}
            tone="success"
          />
        ) : null}
        {!isGuidedDemoWorkspace && provenance?.evaluation ? (
          <DriftEvaluationCard evaluation={provenance.evaluation} workspaceSlug={workspaceSlug} />
        ) : null}
        {alerts.length === 0 ? <p>{isGuidedDemoWorkspace ? messages.drift.none : messages.drift.noneImported}</p> : null}
        {alerts.map((alert) => (
          <AlertDetail key={alert.id} alert={alert} workspaceSlug={workspaceSlug} />
        ))}
      </section>
    </main>
  );
}
