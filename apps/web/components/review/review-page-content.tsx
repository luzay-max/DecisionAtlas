"use client";

import React from "react";

import { ReviewDecision } from "../../lib/api";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
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

  return (
    <main className="page-shell">
      <section className="panel">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/review" />
        <p className="eyebrow">{messages.review.eyebrow}</p>
        <h1>{messages.review.title}</h1>
        <p>{messages.review.lede}</p>
        {decisions.length === 0 ? (
          <p>
            {workspaceSlug === "demo-workspace" ? messages.review.emptyDemo : messages.review.emptyImported}
          </p>
        ) : null}
        <ReviewList decisions={decisions} workspaceSlug={workspaceSlug} />
      </section>
    </main>
  );
}
