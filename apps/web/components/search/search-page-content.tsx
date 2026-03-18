import React from "react";

import { QueryForm } from "./query-form";

export function SearchPageContent() {
  return (
    <main className="page-shell">
      <section className="panel">
        <p className="eyebrow">Why Search</p>
        <h1>Ask why a decision was made</h1>
        <p className="lede">
          Start with a demo question, then check whether the answer is backed by citations or correctly fails closed.
        </p>
        <ul className="stack" aria-label="Example questions">
          <li>why use redis cache</li>
          <li>why is redis cache-only</li>
          <li>why do candidate decisions need review</li>
        </ul>
        <QueryForm />
      </section>
    </main>
  );
}
