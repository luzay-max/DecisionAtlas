import React from "react";

import { SearchPageContent } from "../../components/search/search-page-content";
import { getDashboardSummary } from "../../lib/api";

export default async function SearchPage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  const workspaceSlug = params.workspace ?? "demo-workspace";
  const summary = await getDashboardSummary(workspaceSlug);
  return <SearchPageContent workspaceSlug={workspaceSlug} summary={summary} />;
}
