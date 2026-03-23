"use client";

import React from "react";

import { ReviewDecision } from "../../lib/api";
import { GuidedDemoPanel } from "../guided-demo/guided-demo-panel";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { ProvenanceBanner } from "../provenance/provenance-banner";
import { ReviewList } from "./review-list";
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
    <main className="page-shell">
      <section className="panel">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/review" />
        <p className="eyebrow">{messages.review.eyebrow}</p>
        <h1>{messages.review.title}</h1>
        <p>{messages.review.lede}</p>
        <ProvenanceBanner context="review" workspaceMode={inferredWorkspaceMode} />
        {isGuidedDemoWorkspace ? (
          <GuidedDemoPanel
            step={2}
            total={messages.guidedDemo.steps.length}
            title={messages.guidedDemo.reviewTitle}
            description={messages.guidedDemo.reviewDescription}
            steps={messages.guidedDemo.steps}
            status={messages.review.contextDemo}
          />
        ) : null}
        <ReviewList decisions={decisions} workspaceSlug={workspaceSlug} />
      </section>
    </main>
  );
}
