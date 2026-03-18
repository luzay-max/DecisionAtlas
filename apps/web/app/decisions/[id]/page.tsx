import React from "react";

import { DecisionCard } from "../../../components/decisions/decision-card";
import { SourceRefList } from "../../../components/decisions/source-ref-list";
import { getDecisionDetail } from "../../../lib/api";

export default async function DecisionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const decision = await getDecisionDetail(id);

  return (
    <main className="page-shell">
      <section className="panel">
        <DecisionCard decision={decision} />
        <SourceRefList sourceRefs={decision.source_refs} />
      </section>
    </main>
  );
}
