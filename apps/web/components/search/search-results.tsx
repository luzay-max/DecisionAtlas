"use client";

import React from "react";

import { WhyAnswerResponse } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";
import { ProvenanceBanner } from "../provenance/provenance-banner";

export function SearchResults({ result }: { result: WhyAnswerResponse }) {
  const { messages } = useI18n();
  const answerContext = result.answer_context;

  return (
    <section className="card">
      <p className="eyebrow">{messages.search.answer}</p>
      {answerContext ? (
        <ProvenanceBanner
          workspaceMode={answerContext.workspace_mode}
          sourceSummary={answerContext.source_summary}
          context="answer"
        />
      ) : null}
      <p>
        <strong>{messages.search.status}:</strong>{" "}
        {messages.status[result.status as keyof typeof messages.status] ?? result.status}
      </p>
      {answerContext?.workspace_readiness ? (
        <p>
          <strong>{messages.dashboard.nextAction}:</strong>{" "}
          {messages.importedReadiness.actions[
            answerContext.workspace_readiness.next_action as keyof typeof messages.importedReadiness.actions
          ] ?? answerContext.workspace_readiness.next_action}
        </p>
      ) : null}
      <p>{result.answer}</p>
      {result.citations.length === 0 ? (
        <p>{messages.search.noCitations}</p>
      ) : null}
      <div className="stack">
        {result.citations.map((citation, index) => (
          <article key={`${citation.quote}-${index}`} className="source-ref">
            <blockquote>{citation.quote}</blockquote>
            {citation.url ? (
              <a href={citation.url} target="_blank" rel="noreferrer">
                {citation.url}
              </a>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
