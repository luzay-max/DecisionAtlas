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
  const alerts = await getDriftAlerts(workspaceSlug);
  return <DriftPageContent alerts={alerts} workspaceSlug={workspaceSlug} />;
}
