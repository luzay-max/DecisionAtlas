"use client";

import React, { useState } from "react";

import { askWhy, WhyAnswerResponse } from "../../lib/api";
import { SearchResults } from "./search-results";
import { useI18n } from "../i18n/language-provider";

export function QueryForm({
  workspaceSlug,
  initialQuestion = "why use redis cache",
}: {
  workspaceSlug: string;
  initialQuestion?: string;
}) {
  const { messages } = useI18n();
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
      setError(messages.search.error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <form className="search-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>{messages.search.askWhy}</span>
          <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={messages.search.placeholder} />
        </label>
        <button type="submit">{loading ? messages.search.searching : messages.search.search}</button>
      </form>
      {!result && !error ? <p>{messages.search.intro}</p> : null}
      {error ? <p>{error}</p> : null}
      {result ? <SearchResults result={result} /> : null}
    </div>
  );
}
