import React from "react";

import { TimelineList } from "../../components/timeline/timeline-list";
import { getTimeline, TimelineItem } from "../../lib/api";

export function TimelinePageContent({ items }: { items: TimelineItem[] }) {
  return (
    <main className="page-shell">
      <section className="panel">
        <p className="eyebrow">Decision Timeline</p>
        <h1>Accepted engineering decisions over time</h1>
        <TimelineList items={items} />
      </section>
    </main>
  );
}

export default async function TimelinePage() {
  const items = await getTimeline("demo-workspace");
  return <TimelinePageContent items={items} />;
}
