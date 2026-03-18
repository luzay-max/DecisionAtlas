import React from "react";

import { QueryForm } from "../../components/search/query-form";

export function SearchPageContent() {
  return (
    <main className="page-shell">
      <section className="panel">
        <p className="eyebrow">Why Search</p>
        <h1>Ask why a decision was made</h1>
        <QueryForm />
      </section>
    </main>
  );
}

export default function SearchPage() {
  return <SearchPageContent />;
}
