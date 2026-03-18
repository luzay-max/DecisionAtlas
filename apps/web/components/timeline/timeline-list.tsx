import React from "react";

import { TimelineItem } from "../../lib/api";

export function TimelineList({ items }: { items: TimelineItem[] }) {
  return (
    <div className="stack">
      {items.map((item) => (
        <article key={item.id} className="card">
          <div className="card-head">
            <div>
              <p className="eyebrow">{item.created_at ? new Date(item.created_at).toLocaleDateString() : "Undated"}</p>
              <h2>{item.title}</h2>
            </div>
            <span className="badge">{item.review_state}</span>
          </div>
          <p><strong>Problem:</strong> {item.problem}</p>
          <p><strong>Chosen option:</strong> {item.chosen_option}</p>
          <p><strong>Tradeoffs:</strong> {item.tradeoffs}</p>
        </article>
      ))}
    </div>
  );
}
