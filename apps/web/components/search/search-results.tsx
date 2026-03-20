"use client";

import React from "react";

import { WhyAnswerResponse } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function SearchResults({ result }: { result: WhyAnswerResponse }) {
  const { messages } = useI18n();
  return (
    <section className="card">
      <p className="eyebrow">{messages.search.answer}</p>
      <p>
        <strong>{messages.search.status}:</strong>{" "}
        {messages.status[result.status as keyof typeof messages.status] ?? result.status}
      </p>
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
