import React from "react";

export default function HomePage() {
  return (
    <main className="home">
      <div className="panel">
        <p className="eyebrow">DecisionAtlas</p>
        <h1>Engineering decision memory with citations.</h1>
        <p className="lede">
          Import repository context, review extracted decisions, and answer why-questions with traceable evidence.
        </p>
        <ul className="pill-row" aria-label="MVP concepts">
          <li>Import</li>
          <li>Decisions</li>
          <li>Why</li>
        </ul>
      </div>
    </main>
  );
}
