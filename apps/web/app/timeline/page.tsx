import React from "react";

import { ScopedUnavailable } from "../../components/auth/scoped-unavailable";
import { TimelinePageContent } from "../../components/timeline/timeline-page-content";
import { getTimeline } from "../../lib/api";

export default async function TimelinePage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  const workspaceSlug = params.workspace ?? "demo-workspace";
  try {
    const timeline = await getTimeline(workspaceSlug);
    return <TimelinePageContent timeline={timeline} workspaceSlug={workspaceSlug} />;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load timeline";
    return <ScopedUnavailable workspaceSlug={workspaceSlug} message={message} />;
  }
}
