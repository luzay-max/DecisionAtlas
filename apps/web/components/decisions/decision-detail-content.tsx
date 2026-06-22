"use client";

import React from "react";

import { DecisionCard } from "./decision-card";
import { SourceRefList } from "./source-ref-list";
import { GlobalSidebar } from "../navigation/global-sidebar";
import { DecisionDetail } from "../../lib/api";

export function DecisionDetailContent({
  decision,
  workspaceSlug,
}: {
  decision: DecisionDetail;
  workspaceSlug: string;
}) {
  return (
    <>
      <GlobalSidebar workspaceSlug={workspaceSlug} />
      <main className="page-with-sidebar">
        <section className="panel">
          <DecisionCard decision={decision} />
          <SourceRefList sourceRefs={decision.source_refs} />
        </section>
      </main>
    </>
  );
}
