import React from "react";

import { DemoWorkspaceNav } from "../../components/navigation/demo-workspace-nav";
import { TimelineList } from "../../components/timeline/timeline-list";
import { getTimeline, TimelineItem } from "../../lib/api";

export function TimelinePageContent({ items, workspaceSlug }: { items: TimelineItem[]; workspaceSlug: string }) {
  return (
    <main className="page-shell">
      <section className="panel">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/timeline" />
        <p className="eyebrow">Decision Timeline</p>
        <h1>Accepted engineering decisions over time</h1>
        <TimelineList items={items} workspaceSlug={workspaceSlug} />
      </section>
    </main>
  );
}

export default async function TimelinePage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  const workspaceSlug = params.workspace ?? "demo-workspace";
  const items = await getTimeline(workspaceSlug);
  return <TimelinePageContent items={items} workspaceSlug={workspaceSlug} />;
}
