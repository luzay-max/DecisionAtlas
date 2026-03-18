"use client";

import React, { useState } from "react";

import { askWhy, WhyAnswerResponse } from "../../lib/api";

export function QueryForm({ initialQuestion = "why use redis cache" }: { initialQuestion?: string }) {
  const [question, setQuestion] = useState(initialQuestion);
  const [result, setResult] = useState<WhyAnswerResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await askWhy("demo-workspace", question);
      setResult(response);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <form className="search-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Ask why</span>
          <input value={question} onChange={(event) => setQuestion(event.target.value)} />
        </label>
        <button type="submit">{loading ? "Searching..." : "Search"}</button>
      </form>
      {result ? (
        <section className="card">
          <p className="eyebrow">Answer</p>
          <p>{result.answer}</p>
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
      ) : null}
    </div>
  );
}
