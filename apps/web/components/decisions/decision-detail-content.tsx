"use client";

import React from "react";

import { DecisionCard } from "./decision-card";
import { SourceRefList } from "./source-ref-list";
import { GlobalSidebar } from "../navigation/global-sidebar";
import { WorkspaceContextBanner } from "../navigation/workspace-context-banner";
import { DecisionDetail } from "../../lib/api";
import Link from "next/link";

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
        <section className="panel stack">
          <WorkspaceContextBanner
            workspaceSlug={workspaceSlug}
            current="Decision detail"
            description="One decision object with evidence, review state, source references, and next actions."
          />
          <DecisionCard decision={decision} />
          <SourceRefList sourceRefs={decision.source_refs} />
          <section className="card">
            <p className="eyebrow">Decision next actions</p>
            <h2>Continue from this decision</h2>
            <p className="muted">
              Keep the same workspace context while you continue review, ask why, inspect drift, or verify release evidence.
            </p>
            <div className="action-row">
              <Link href={`/review?workspace=${encodeURIComponent(workspaceSlug)}`} className="action-link action-link-primary">
                Continue review
              </Link>
              <Link href={`/search?workspace=${encodeURIComponent(workspaceSlug)}`} className="action-link">
                Ask why
              </Link>
              <Link href={`/timeline?workspace=${encodeURIComponent(workspaceSlug)}`} className="action-link">
                Timeline
              </Link>
              <Link href={`/drift?workspace=${encodeURIComponent(workspaceSlug)}`} className="action-link">
                Drift
              </Link>
              <Link href="/evidence" className="action-link">
                Evidence Center
              </Link>
            </div>
          </section>
        </section>
      </main>
    </>
  );
}
