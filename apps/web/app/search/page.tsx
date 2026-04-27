import React from "react";

import { ScopedUnavailable } from "../../components/auth/scoped-unavailable";
import { SearchPageContent } from "../../components/search/search-page-content";
import { getDashboardSummary } from "../../lib/api";

export default async function SearchPage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  const workspaceSlug = params.workspace ?? "demo-workspace";
  try {
    const summary = await getDashboardSummary(workspaceSlug);
    return <SearchPageContent workspaceSlug={workspaceSlug} summary={summary} />;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load workspace summary";
    return <ScopedUnavailable workspaceSlug={workspaceSlug} message={message} />;
  }
}
