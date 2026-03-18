"use client";

import React, { useState } from "react";

import { askWhy, WhyAnswerResponse } from "../../lib/api";
import { SearchResults } from "./search-results";

export function QueryForm({
  workspaceSlug,
  initialQuestion = "why use redis cache",
}: {
  workspaceSlug: string;
  initialQuestion?: string;
}) {
  const [question, setQuestion] = useState(initialQuestion);
  const [result, setResult] = useState<WhyAnswerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await askWhy(workspaceSlug, question);
      setResult(response);
    } catch {
      setResult(null);
      setError("Why search is unavailable right now. Confirm the API, engine, and provider configuration.");
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
      {!result && !error ? <p>Ask one of the example questions after the demo import finishes.</p> : null}
      {error ? <p>{error}</p> : null}
      {result ? <SearchResults result={result} /> : null}
    </div>
  );
}
