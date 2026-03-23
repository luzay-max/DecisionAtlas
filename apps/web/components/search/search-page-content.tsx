"use client";

import React from "react";

import { DashboardSummary } from "../../lib/api";
import { GuidedDemoPanel } from "../guided-demo/guided-demo-panel";
import { ImportedReadinessCard } from "../imported/imported-readiness-card";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { QueryForm } from "./query-form";
import { useI18n } from "../i18n/language-provider";

export function SearchPageContent({
  workspaceSlug,
  summary,
}: {
  workspaceSlug: string;
  summary: DashboardSummary;
}) {
  const { messages } = useI18n();
  const isGuidedDemoWorkspace = workspaceSlug === "demo-workspace";

  return (
    <main className="page-shell">
      <section className="panel">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/search" />
        <p className="eyebrow">{messages.search.eyebrow}</p>
        <h1>{messages.search.title}</h1>
        <p className="lede">{messages.search.lede}</p>
        {isGuidedDemoWorkspace ? (
          <GuidedDemoPanel
            step={3}
            total={messages.guidedDemo.steps.length}
            title={messages.guidedDemo.searchTitle}
            description={messages.guidedDemo.searchDescription}
            steps={messages.guidedDemo.steps}
          />
        ) : null}
        {!isGuidedDemoWorkspace && summary.workspace_readiness ? (
          <ImportedReadinessCard readiness={summary.workspace_readiness} workspaceSlug={workspaceSlug} />
        ) : null}
        <h2>{messages.search.examplesTitle}</h2>
        <ul className="stack" aria-label={messages.search.examplesTitle}>
          {messages.search.examples.map((example) => (
            <li key={example}>{example}</li>
          ))}
        </ul>
        <QueryForm workspaceSlug={workspaceSlug} />
      </section>
    </main>
  );
}
