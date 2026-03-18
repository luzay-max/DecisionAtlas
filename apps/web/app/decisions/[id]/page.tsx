import React from "react";

import { DecisionCard } from "../../../components/decisions/decision-card";
import { SourceRefList } from "../../../components/decisions/source-ref-list";
import { DemoWorkspaceNav } from "../../../components/navigation/demo-workspace-nav";
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

  return (
    <main className="page-shell">
      <section className="panel">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/review" />
        <DecisionCard decision={decision} />
        <SourceRefList sourceRefs={decision.source_refs} />
      </section>
    </main>
  );
}
