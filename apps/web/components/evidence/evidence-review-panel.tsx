"use client";

import React from "react";

import { SourceRef } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

function safeExternalUrl(value: string | null | undefined): string | null {
  if (!value) return null;
  try {
    const parsed = new URL(value);
    if ((parsed.protocol !== "https:" && parsed.protocol !== "http:") || parsed.username || parsed.password) {
      return null;
    }
    return parsed.href;
  } catch {
    return null;
  }
}

function hasQuote(sourceRef: SourceRef): boolean {
  return typeof sourceRef.quote === "string" && sourceRef.quote.trim().length > 0;
}

function hasSpan(sourceRef: SourceRef): boolean {
  return Number.isInteger(sourceRef.span_start)
    && Number.isInteger(sourceRef.span_end)
    && (sourceRef.span_start ?? -1) >= 0
    && (sourceRef.span_end ?? -1) >= (sourceRef.span_start ?? 0);
}

function metric(label: string, present: number, total: number) {
  return (
    <div className="evidence-review-metric" key={label}>
      <span>{label}</span>
      <strong>{present} / {total}</strong>
    </div>
  );
}

export function EvidenceReviewPanel({
  sourceRefs,
  totalSourceCount,
  compact = false,
}: {
  sourceRefs: SourceRef[];
  totalSourceCount?: number;
  compact?: boolean;
}) {
  const { messages } = useI18n();
  const total = Math.max(totalSourceCount ?? sourceRefs.length, sourceRefs.length);
  const quoteCount = sourceRefs.filter(hasQuote).length;
  const linkCount = sourceRefs.filter((sourceRef) => safeExternalUrl(sourceRef.url)).length;
  const spanCount = sourceRefs.filter(hasSpan).length;
  const metrics = [
    metric(messages.evidenceReview.quoteCoverage, quoteCount, sourceRefs.length),
    metric(messages.evidenceReview.linkCoverage, linkCount, sourceRefs.length),
    metric(messages.evidenceReview.spanCoverage, spanCount, sourceRefs.length),
  ];

  return (
    <section
      className={"evidence-review-panel" + (compact ? " evidence-review-panel-compact" : "")}
      aria-labelledby={compact ? undefined : "evidence-review-title"}
    >
      <div className="evidence-review-heading">
        <div>
          <p className="eyebrow">{messages.evidenceReview.eyebrow}</p>
          <h2 id={compact ? undefined : "evidence-review-title"}>
            {compact ? messages.evidenceReview.title : messages.detail.sourceRefs}
          </h2>
          <p className="evidence-review-source-count">
            {messages.evidenceReview.sourceCount.replace("{count}", String(total))}
            {compact && sourceRefs.length < total
              ? " · " + messages.evidenceReview.previewCount.replace("{count}", String(sourceRefs.length))
              : ""}
          </p>
        </div>
        <span className="evidence-review-scope-badge">{messages.evidenceReview.metadataOnly}</span>
      </div>

      <div className="evidence-review-metrics" aria-label={messages.evidenceReview.summaryLabel}>
        {metrics}
      </div>

      {compact ? (
        <>
          {sourceRefs.length === 0 ? (
            <p className="muted">
              {total > 0 ? messages.evidenceReview.noPreviewRefs : messages.evidenceReview.noSourceRefs}
            </p>
          ) : null}
          <p className="evidence-review-boundary" role="note">{messages.evidenceReview.queueNotice}</p>
          <p className="evidence-review-unverified">{messages.evidenceReview.noIndependentReview}</p>
        </>
      ) : (
        <>
          {sourceRefs.length === 0 ? (
            <p className="muted">{messages.evidenceReview.noSourceRefs}</p>
          ) : (
            <div className="evidence-review-sources">
              {sourceRefs.map((sourceRef) => {
                const quoteAvailable = hasQuote(sourceRef);
                const externalUrl = safeExternalUrl(sourceRef.url);
                const spanAvailable = hasSpan(sourceRef);
                const sourceLabel = messages.evidenceReview.sourceLabel.replace("{id}", String(sourceRef.id));

                return (
                  <article className="evidence-source-card" key={sourceRef.id}>
                    <div className="evidence-source-heading">
                      <h3>{sourceLabel}</h3>
                      <div className="evidence-source-statuses">
                        <span className={"evidence-status" + (quoteAvailable ? " evidence-status-present" : " evidence-status-missing")}>
                          {quoteAvailable ? messages.evidenceReview.quoteAvailable : messages.evidenceReview.quoteMissing}
                        </span>
                        <span className={"evidence-status" + (externalUrl ? " evidence-status-present" : " evidence-status-missing")}>
                          {externalUrl ? messages.evidenceReview.linkAvailable : messages.evidenceReview.linkMissing}
                        </span>
                        <span className={"evidence-status" + (spanAvailable ? " evidence-status-present" : " evidence-status-missing")}>
                          {spanAvailable ? messages.evidenceReview.spanAvailable : messages.evidenceReview.spanMissing}
                        </span>
                      </div>
                    </div>
                    {quoteAvailable ? (
                      <blockquote className="evidence-source-quote">{sourceRef.quote}</blockquote>
                    ) : (
                      <p className="muted">{messages.evidenceReview.noQuote}</p>
                    )}
                    {spanAvailable ? (
                      <p className="evidence-source-span">
                        <strong>{messages.evidenceReview.recordedSpan}:</strong>{" "}
                        {sourceRef.span_start}–{sourceRef.span_end}
                      </p>
                    ) : null}
                    {externalUrl ? (
                      <a href={externalUrl} target="_blank" rel="noopener noreferrer" className="evidence-source-link">
                        {messages.evidenceReview.openSource}
                        <span className="evidence-source-url">{externalUrl}</span>
                      </a>
                    ) : null}
                  </article>
                );
              })}
            </div>
          )}
          <p className="evidence-review-boundary" role="note">{messages.evidenceReview.limitation}</p>
          <p className="evidence-review-unverified">{messages.evidenceReview.noIndependentReview}</p>
        </>
      )}
    </section>
  );
}
