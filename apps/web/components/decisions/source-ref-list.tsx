import React from "react";

import { SourceRef } from "../../lib/api";

export function SourceRefList({ sourceRefs }: { sourceRefs: SourceRef[] }) {
  return (
    <section className="stack">
      <h2>Source References</h2>
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
