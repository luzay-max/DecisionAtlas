"use client";

import React from "react";

import { useI18n } from "../i18n/language-provider";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { TimelineList } from "./timeline-list";
import { TimelineResponse } from "../../lib/api";
import { ProvenanceBanner } from "../provenance/provenance-banner";

export function TimelinePageContent({
  timeline,
  workspaceSlug,
}: {
  timeline: TimelineResponse | Array<TimelineResponse["items"][number]>;
  workspaceSlug: string;
}) {
  const { messages } = useI18n();
  const items = Array.isArray(timeline) ? timeline : timeline.items;
  const provenance = Array.isArray(timeline) ? null : timeline;

  return (
    <main className="page-shell">
      <section className="panel">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/timeline" />
        <p className="eyebrow">{messages.timeline.eyebrow}</p>
        <h1>{messages.timeline.title}</h1>
        {provenance ? (
          <ProvenanceBanner
            workspaceMode={provenance.workspace_mode}
            sourceSummary={provenance.source_summary}
            context="timeline"
          />
        ) : null}
        <TimelineList items={items} workspaceSlug={workspaceSlug} />
      </section>
    </main>
  );
}
