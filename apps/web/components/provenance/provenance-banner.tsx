"use client";

import React from "react";

import { WorkspaceMode } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function ProvenanceBanner({
  workspaceMode,
  sourceSummary,
  context,
}: {
  workspaceMode: WorkspaceMode;
  sourceSummary?: string;
  context: "dashboard" | "answer" | "timeline" | "drift" | "detail";
}) {
  const { messages } = useI18n();
  const modeLabel = messages.provenance.modes[workspaceMode] ?? workspaceMode;
  const contextLabel = messages.provenance.contexts[context];
  const summary = messages.provenance.summaries[workspaceMode] ?? sourceSummary ?? "";

  return (
    <div className="card provenance-banner">
      <p className="eyebrow">{contextLabel}</p>
      <p>
        <strong>{messages.provenance.workspaceType}:</strong> {modeLabel}
      </p>
      <p>
        <strong>{messages.provenance.dataSource}:</strong> {summary}
      </p>
    </div>
  );
}
