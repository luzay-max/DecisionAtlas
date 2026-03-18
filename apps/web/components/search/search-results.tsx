import React from "react";

import { WhyAnswerResponse } from "../../lib/api";

export function SearchResults({ result }: { result: WhyAnswerResponse }) {
  return (
    <section className="card">
      <p className="eyebrow">Answer</p>
      <p>{result.answer}</p>
      <div className="stack">
        {result.citations.map((citation, index) => (
          <article key={`${citation.quote}-${index}`} className="source-ref">
            <blockquote>{citation.quote}</blockquote>
          </article>
        ))}
      </div>
    </section>
  );
}
