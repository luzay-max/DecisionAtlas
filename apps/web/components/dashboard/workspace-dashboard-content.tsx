"use client";

import Link from "next/link";
import React from "react";

import { DashboardSummary } from "../../lib/api";
import { GuidedDemoPanel } from "../guided-demo/guided-demo-panel";
import { DemoImportButton } from "./demo-import-button";
import { KpiStrip } from "./kpi-strip";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { RecentAlerts } from "./recent-alerts";
import { useI18n } from "../i18n/language-provider";
import { ImportedReadinessCard } from "../imported/imported-readiness-card";
import { ProvenanceBanner } from "../provenance/provenance-banner";

export function WorkspaceDashboardContent({ summary }: { summary: DashboardSummary }) {
  const { messages } = useI18n();
  const guidedDemoSteps = messages.guidedDemo.steps;
  const isGuidedDemoWorkspace = summary.workspace_slug === "demo-workspace";
  const latestImportStatus = summary.latest_import
    ? (messages.status[summary.latest_import.status as keyof typeof messages.status] ?? summary.latest_import.status)
    : null;
  const latestImportMode = summary.latest_import
    ? (messages.dashboard.importMode[summary.latest_import.mode as keyof typeof messages.dashboard.importMode] ??
      summary.latest_import.mode)
    : null;
  const latestImportSummary = summary.latest_import?.summary;
  const latestImportStage = latestImportSummary?.stage
    ? (messages.status[latestImportSummary.stage as keyof typeof messages.status] ?? latestImportSummary.stage)
    : null;
  const latestImportOutcome = latestImportSummary?.outcome
    ? (messages.status[latestImportSummary.outcome as keyof typeof messages.status] ?? latestImportSummary.outcome)
    : null;
  const latestImportFailure = latestImportSummary?.failure_category
    ? (messages.status[latestImportSummary.failure_category as keyof typeof messages.status] ??
      latestImportSummary.failure_category)
    : null;
  const skippedDocumentCount = latestImportSummary
    ? Object.values(latestImportSummary.document_summary?.skipped ?? {}).reduce((total, count) => total + count, 0)
    : 0;
  const hasAcceptedOrSupersededDecisions =
    summary.decision_counts.accepted > 0 || summary.decision_counts.superseded > 0;
  const showLowSignalHint =
    summary.workspace_mode !== "demo" &&
    summary.decision_counts.candidate === 0 &&
    !hasAcceptedOrSupersededDecisions &&
    summary.latest_import?.status !== "failed" &&
    latestImportSummary?.outcome === "insufficient_evidence";
  const isImportRunning = summary.import_status === "queued" || summary.import_status === "running";
  const isImportFailed = summary.latest_import?.status === "failed";
  let guidedDemoStep = 1;
  let guidedDemoTitle: string = messages.guidedDemo.dashboardTitle;
  let guidedDemoDescription: string = messages.guidedDemo.dashboardDescription;
  let guidedDemoStatus: string = messages.guidedDemo.dashboardReadyStatus;
  let guidedDemoNextHref: string | undefined;
  let guidedDemoNextLabel: string | undefined;
  let guidedDemoTone: "default" | "success" | "warning" = "default";

  if (isImportRunning) {
    guidedDemoStatus = messages.guidedDemo.importInProgressStatus;
  } else if (isImportFailed) {
    guidedDemoTone = "warning";
    guidedDemoStatus = messages.guidedDemo.importFailedStatus;
  } else if (summary.decision_counts.candidate > 0) {
    guidedDemoStep = 2;
    guidedDemoTitle = messages.guidedDemo.reviewTitle;
    guidedDemoDescription = messages.guidedDemo.reviewDescription;
    guidedDemoNextHref = `/review?workspace=${encodeURIComponent(summary.workspace_slug)}`;
    guidedDemoNextLabel = messages.dashboard.reviewCandidates;
  } else if (summary.decision_counts.accepted > 0) {
    guidedDemoStep = 3;
    guidedDemoTitle = messages.guidedDemo.searchTitle;
    guidedDemoDescription = messages.guidedDemo.searchDescription;
    guidedDemoNextHref = `/search?workspace=${encodeURIComponent(summary.workspace_slug)}`;
    guidedDemoNextLabel = messages.guidedDemo.searchNext;
    guidedDemoStatus = messages.guidedDemo.reviewCompletedStatus;
    guidedDemoTone = "success";
  }

  return (
    <main className="page-shell">
      <section className="panel stack">
        <DemoWorkspaceNav workspaceSlug={summary.workspace_slug} currentPath={`/workspaces/${summary.workspace_slug}`} />
        <div>
          <p className="eyebrow">{messages.dashboard.eyebrow}</p>
          <h1>{summary.workspace_slug}</h1>
          <p>
            {messages.dashboard.demoRepo}: {summary.github_repo}
          </p>
        </div>
        <ProvenanceBanner
          workspaceMode={summary.workspace_mode}
          sourceSummary={summary.source_summary}
          context="dashboard"
        />
        {isGuidedDemoWorkspace ? (
          <GuidedDemoPanel
            step={guidedDemoStep}
            total={guidedDemoSteps.length}
            title={guidedDemoTitle}
            description={guidedDemoDescription}
            steps={guidedDemoSteps}
            status={guidedDemoStatus}
            nextHref={guidedDemoNextHref}
            nextLabel={guidedDemoNextLabel}
            tone={guidedDemoTone}
          />
        ) : null}
        {!isGuidedDemoWorkspace && summary.workspace_readiness ? (
          <ImportedReadinessCard readiness={summary.workspace_readiness} workspaceSlug={summary.workspace_slug} />
        ) : null}
        <DemoImportButton
          workspaceSlug={summary.workspace_slug}
          repo={summary.github_repo}
          latestImport={summary.latest_import}
          importStatus={summary.import_status}
        />
        <div className="action-row">
          <Link href={`/review?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            {messages.dashboard.reviewCandidates}
          </Link>
          <Link href={`/search?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            {messages.dashboard.askWhy}
          </Link>
          <Link href={`/drift?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            {messages.dashboard.inspectDrift}
          </Link>
          <Link href={`/timeline?workspace=${encodeURIComponent(summary.workspace_slug)}`} className="action-link">
            {messages.dashboard.openTimeline}
          </Link>
        </div>
        {summary.latest_import ? (
          <div className="stack">
            <p className="eyebrow">{messages.dashboard.latestImport}</p>
            <p>
              {latestImportStatus} · {latestImportMode} · {summary.latest_import.imported_count}{" "}
              {messages.kpi.artifacts}
            </p>
            {latestImportStage ? (
              <p>
                {messages.dashboard.stageLabel}: {latestImportStage}
              </p>
            ) : null}
            {latestImportOutcome ? (
              <p>
                {messages.dashboard.outcomeLabel}: {latestImportOutcome}
              </p>
            ) : null}
            {latestImportFailure ? (
              <p>
                {messages.dashboard.failureLabel}: {latestImportFailure}
              </p>
            ) : null}
            {latestImportSummary?.document_summary ? (
              <p>
                {messages.dashboard.docImportSummary
                  .replace("{docs}", String(latestImportSummary.document_summary.imported))
                  .replace("{selected}", String(latestImportSummary.document_summary.selected))
                  .replace("{skipped}", String(skippedDocumentCount))}
              </p>
            ) : null}
            {latestImportSummary?.evidence_summary ? (
              <p>
                {messages.dashboard.evidenceContributionSummary
                  .replace("{decisions}", String(latestImportSummary.evidence_summary.reviewable_decisions))
                  .replace(
                    "{signals}",
                    Object.entries(latestImportSummary.evidence_summary.decision_source_types)
                      .map(([artifactType, count]) => `${artifactType}:${count}`)
                      .join(", ") || messages.common.noData
                  )}
              </p>
            ) : null}
            {summary.latest_import.error_message ? <p>{summary.latest_import.error_message}</p> : null}
          </div>
        ) : null}
        {showLowSignalHint ? <p>{messages.dashboard.lowSignalHint}</p> : null}
        <KpiStrip summary={summary} />
        <RecentAlerts summary={summary} />
      </section>
    </main>
  );
}
