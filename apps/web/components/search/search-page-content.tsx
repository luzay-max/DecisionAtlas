"use client";

import React from "react";

import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { QueryForm } from "./query-form";
import { useI18n } from "../i18n/language-provider";

export function SearchPageContent({ workspaceSlug }: { workspaceSlug: string }) {
  const { messages } = useI18n();

  return (
    <main className="page-shell">
      <section className="panel">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/search" />
        <p className="eyebrow">{messages.search.eyebrow}</p>
        <h1>{messages.search.title}</h1>
        <p className="lede">{messages.search.lede}</p>
        <h2>{messages.search.examplesTitle}</h2>
        <ul className="stack" aria-label={messages.search.examplesTitle}>
          {messages.search.examples.map((example) => (
            <li key={example}>{example}</li>
          ))}
        </ul>
        <QueryForm workspaceSlug={workspaceSlug} />
      </section>
    </main>
  );
}
