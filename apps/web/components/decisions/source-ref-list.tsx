"use client";

import React from "react";

import { SourceRef } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function SourceRefList({ sourceRefs }: { sourceRefs: SourceRef[] }) {
  const { messages } = useI18n();
  return (
    <section className="stack">
      <h2>{messages.detail.sourceRefs}</h2>
      {sourceRefs.map((sourceRef) => (
        <article key={sourceRef.id} className="source-ref">
          <blockquote>{sourceRef.quote}</blockquote>
          {sourceRef.url ? (
            <a href={sourceRef.url} target="_blank" rel="noreferrer">
              {sourceRef.url}
            </a>
          ) : null}
        </article>
      ))}
    </section>
  );
}
