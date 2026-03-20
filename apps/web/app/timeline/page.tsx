import React from "react";

import { TimelinePageContent } from "../../components/timeline/timeline-page-content";
import { getTimeline } from "../../lib/api";

export default async function TimelinePage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  const workspaceSlug = params.workspace ?? "demo-workspace";
  const timeline = await getTimeline(workspaceSlug);
  return <TimelinePageContent timeline={timeline} workspaceSlug={workspaceSlug} />;
}
