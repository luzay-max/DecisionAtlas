import React from "react";

import { ScopedUnavailable } from "../../components/auth/scoped-unavailable";
import { DriftPageContent } from "../../components/drift/drift-page-content";
import { getDriftAlerts } from "../../lib/api";

export default async function DriftPage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  const workspaceSlug = params.workspace ?? "demo-workspace";
  try {
    const drift = await getDriftAlerts(workspaceSlug);
    return <DriftPageContent drift={drift} workspaceSlug={workspaceSlug} />;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load drift alerts";
    return <ScopedUnavailable workspaceSlug={workspaceSlug} message={message} />;
  }
}
