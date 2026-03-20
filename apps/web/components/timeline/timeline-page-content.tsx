"use client";

import React from "react";

import { useI18n } from "../i18n/language-provider";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { TimelineList } from "./timeline-list";
import { TimelineItem } from "../../lib/api";

export function TimelinePageContent({ items, workspaceSlug }: { items: TimelineItem[]; workspaceSlug: string }) {
  const { messages } = useI18n();

  return (
    <main className="page-shell">
      <section className="panel">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/timeline" />
        <p className="eyebrow">{messages.timeline.eyebrow}</p>
        <h1>{messages.timeline.title}</h1>
        <TimelineList items={items} workspaceSlug={workspaceSlug} />
      </section>
    </main>
  );
}
