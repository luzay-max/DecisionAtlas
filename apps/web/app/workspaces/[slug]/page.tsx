import React from "react";

import { ScopedUnavailable } from "../../../components/auth/scoped-unavailable";
import { WorkspaceDashboardContent } from "../../../components/dashboard/workspace-dashboard-content";
import { getDashboardSummary } from "../../../lib/api";

export default async function WorkspaceDashboardPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams?: Promise<{ job?: string }>;
}) {
  const { slug } = await params;
  const query = (await searchParams) ?? {};
  try {
    const summary = await getDashboardSummary(slug);
    return <WorkspaceDashboardContent summary={summary} initialJobId={query.job ?? null} />;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load dashboard summary";
    return <ScopedUnavailable workspaceSlug={slug} message={message} />;
  }
}
