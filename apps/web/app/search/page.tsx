import React from "react";

import { SearchPageContent } from "../../components/search/search-page-content";

export default async function SearchPage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  return <SearchPageContent workspaceSlug={params.workspace ?? "demo-workspace"} />;
}
