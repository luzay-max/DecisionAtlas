"use client";

import React from "react";

import { ReviewDecision } from "../../lib/api";
import { GuidedDemoPanel } from "../guided-demo/guided-demo-panel";
import { GlobalSidebar } from "../navigation/global-sidebar";
import { ProvenanceBanner } from "../provenance/provenance-banner";
import { ReviewAuditPanel } from "./review-audit-panel";
import { ReviewList } from "./review-list";
import { WorkspaceContextBanner } from "../navigation/workspace-context-banner";
import { useI18n } from "../i18n/language-provider";

export function ReviewPageContent({
  decisions,
  workspaceSlug,
}: {
  decisions: ReviewDecision[];
  workspaceSlug: string;
}) {
  const { messages } = useI18n();
  const inferredWorkspaceMode = workspaceSlug === "demo-workspace" ? "demo" : "imported";
  const isGuidedDemoWorkspace = workspaceSlug === "demo-workspace";

  return (
    <>
      <GlobalSidebar workspaceSlug={workspaceSlug} />
      <main className="page-with-sidebar">
        <section className="panel">
          <WorkspaceContextBanner
            workspaceSlug={workspaceSlug}
            current="Review queue"
            description="Candidate decisions that need human acceptance, rejection, or supersession."
          />
          <p className="eyebrow">{messages.review.eyebrow}</p>
          <h1>{messages.review.title}</h1>
          <p>{messages.review.lede}</p>
          <ProvenanceBanner context="review" workspaceMode={inferredWorkspaceMode} />
          <ReviewAuditPanel decisions={decisions} />
          {isGuidedDemoWorkspace ? (
            <GuidedDemoPanel
              step={2}
              total={messages.guidedDemo.steps.length}
              title={messages.guidedDemo.reviewTitle}
              description={messages.guidedDemo.reviewDescription}
              steps={messages.guidedDemo.steps}
              status={messages.review.contextDemo}
            />
          ) : decisions.length > 0 ? (
            <div className="callout">
              <p className="eyebrow">{messages.review.candidateDecision}</p>
              <p>{messages.review.importedGuidance}</p>
            </div>
          ) : null}
          <ReviewList decisions={decisions} workspaceSlug={workspaceSlug} />
        </section>
      </main>
    </>
  );
}
