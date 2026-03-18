import React from "react";

import { WhyAnswerResponse } from "../../lib/api";

export function SearchResults({ result }: { result: WhyAnswerResponse }) {
  return (
    <section className="card">
      <p className="eyebrow">Answer</p>
      <p>
        <strong>Status:</strong> {result.status}
      </p>
      <p>{result.answer}</p>
      {result.citations.length === 0 ? (
        <p>No citations were returned. Import more evidence or accept more decisions before trusting this answer.</p>
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
