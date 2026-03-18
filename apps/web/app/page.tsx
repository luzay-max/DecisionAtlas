import React from "react";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="home">
      <div className="panel">
        <p className="eyebrow">DecisionAtlas</p>
        <h1>Engineering decision memory with citations.</h1>
        <p className="lede">
          Import a public GitHub repository, review extracted decisions, answer why-questions with traceable
          evidence, and inspect drift before it turns into accidental architecture change.
        </p>
        <ul className="pill-row" aria-label="MVP concepts">
          <li>Import</li>
          <li>Decisions</li>
          <li>Why</li>
        </ul>
        <ol>
          <li>Run the demo import for the workspace.</li>
          <li>Review the highest-confidence candidate decisions.</li>
          <li>Ask a why-question and inspect drift alerts.</li>
        </ol>
        <p>
          <Link href="/workspaces/demo-workspace">Open the public demo workspace</Link>
        </p>
      </div>
    </main>
  );
}
