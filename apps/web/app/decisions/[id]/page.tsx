import React from "react";

import { DecisionDetailContent } from "../../../components/decisions/decision-detail-content";
import { getDecisionDetail } from "../../../lib/api";

export default async function DecisionDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const { id } = await params;
  const query = (await searchParams) ?? {};
  const workspaceSlug = query.workspace ?? "demo-workspace";
  const decision = await getDecisionDetail(id);

  return <DecisionDetailContent decision={decision} workspaceSlug={workspaceSlug} />;
}
