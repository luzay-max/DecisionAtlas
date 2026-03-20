"use client";

import Link from "next/link";
import React from "react";

import { TimelineItem } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function TimelineList({ items, workspaceSlug }: { items: TimelineItem[]; workspaceSlug: string }) {
  const { language, messages } = useI18n();
  const dateFormatter = new Intl.DateTimeFormat(language === "zh" ? "zh-CN" : "en-US", {
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="stack">
      {items.map((item) => (
        <article key={item.id} className="card">
          <div className="card-head">
            <div>
              <p className="eyebrow">
                {item.created_at ? dateFormatter.format(new Date(item.created_at)) : messages.timeline.undated}
              </p>
              <h2>
                <Link
                  href={`/decisions/${item.id}?workspace=${encodeURIComponent(workspaceSlug)}`}
                  className="title-link"
                >
                  {item.title}
                </Link>
              </h2>
            </div>
            <span className="badge">{messages.status[item.review_state as keyof typeof messages.status] ?? item.review_state}</span>
          </div>
          <p>
            <strong>{messages.timeline.problem}:</strong> {item.problem}
          </p>
          <p>
            <strong>{messages.timeline.chosenOption}:</strong> {item.chosen_option}
          </p>
          <p>
            <strong>{messages.timeline.tradeoffs}:</strong> {item.tradeoffs}
          </p>
        </article>
      ))}
    </div>
  );
}
