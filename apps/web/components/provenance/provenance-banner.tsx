"use client";

import React from "react";

import { WorkspaceMode } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function ProvenanceBanner({
  workspaceMode,
  sourceSummary,
  context,
}: {
  workspaceMode?: WorkspaceMode | null;
  sourceSummary?: string | null;
  context: "dashboard" | "answer" | "timeline" | "drift" | "detail";
}) {
  const { messages } = useI18n();
  const modeLabel = workspaceMode
    ? (messages.provenance.modes[workspaceMode] ?? workspaceMode)
    : messages.common.noData;
  const contextLabel = messages.provenance.contexts[context];
  const summary = workspaceMode
    ? (messages.provenance.summaries[workspaceMode] ?? sourceSummary ?? messages.common.noData)
    : (sourceSummary ?? messages.common.noData);

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
