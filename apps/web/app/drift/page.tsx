import React from "react";

import { DriftPageContent } from "../../components/drift/drift-page-content";
import { getDriftAlerts } from "../../lib/api";

export default async function DriftPage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  const workspaceSlug = params.workspace ?? "demo-workspace";
  const drift = await getDriftAlerts(workspaceSlug);
  return <DriftPageContent drift={drift} workspaceSlug={workspaceSlug} />;
}
