"use client";

import React, { useState } from "react";

import {
  GovernanceDocument,
  GovernanceRule,
  importGovernanceDocument,
  reviewGovernanceRule,
} from "../../lib/api";
import { AdminOnly, ReviewOnly } from "../auth/role-gate";
import { useI18n } from "../i18n/language-provider";

const documentTypes = [
  "standard",
  "coding_guideline",
  "architecture_policy",
  "roadmap",
  "postmortem",
  "checklist",
  "decision_record",
  "anti_pattern",
  "release_policy",
  "security_policy",
];

export function GovernancePageContent({
  initialDocuments,
  initialRules,
}: {
  initialDocuments: GovernanceDocument[];
  initialRules: GovernanceRule[];
}) {
  const { messages } = useI18n();
  const [documents, setDocuments] = useState(initialDocuments);
  const [rules, setRules] = useState(initialRules);
  const [title, setTitle] = useState("");
  const [documentType, setDocumentType] = useState("coding_guideline");
  const [scope, setScope] = useState("all");
  const [sourcePath, setSourcePath] = useState("");
  const [content, setContent] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [reviewingId, setReviewingId] = useState<number | null>(null);

  const pendingRules = rules.filter((rule) => rule.review_state === "pending");
  const acceptedRules = rules.filter((rule) => rule.review_state === "accepted");

  async function handleImport(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const result = await importGovernanceDocument({
        title,
        document_type: documentType,
        scope,
        source_path: sourcePath || undefined,
        content,
      });
      setDocuments([result.document, ...documents]);
      setRules([...result.drafts, ...rules]);
      setTitle("");
      setSourcePath("");
      setContent("");
      setMessage(
        messages.governance.imported
          .replace("{title}", result.document.title)
          .replace("{count}", String(result.drafts.length))
      );
    } catch (error) {
      const detail = error instanceof Error ? error.message : "unknown error";
      setMessage(messages.governance.importFailed.replace("{detail}", detail));
    } finally {
      setLoading(false);
    }
  }

  async function handleReview(ruleId: number, reviewState: "accepted" | "rejected") {
    setReviewingId(ruleId);
    setMessage(null);
    try {
      const updatedRule = await reviewGovernanceRule(ruleId, reviewState);
      setRules(rules.map((rule) => (rule.id === updatedRule.id ? updatedRule : rule)));
    } catch {
      setMessage(messages.governance.reviewFailed);
    } finally {
      setReviewingId(null);
    }
  }

  return (
    <main className="home">
      <div className="panel stack">
        <p className="eyebrow">{messages.governance.eyebrow}</p>
        <h1>{messages.governance.title}</h1>
        <p className="lede">{messages.governance.lede}</p>
        <p>{messages.governance.boundary}</p>

        <AdminOnly>
          <form className="stack" onSubmit={handleImport}>
            <label>
              <strong>{messages.governance.titleLabel}</strong>
              <input value={title} onChange={(event) => setTitle(event.target.value)} required />
            </label>
            <label>
              <strong>{messages.governance.typeLabel}</strong>
              <select value={documentType} onChange={(event) => setDocumentType(event.target.value)}>
                {documentTypes.map((type) => (
                  <option key={type} value={type}>
                    {messages.governance.types[type as keyof typeof messages.governance.types] ?? type}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <strong>{messages.governance.scopeLabel}</strong>
              <input value={scope} onChange={(event) => setScope(event.target.value)} />
            </label>
            <label>
              <strong>{messages.governance.sourcePathLabel}</strong>
              <input value={sourcePath} onChange={(event) => setSourcePath(event.target.value)} />
            </label>
            <label>
              <strong>{messages.governance.contentLabel}</strong>
              <textarea rows={10} value={content} onChange={(event) => setContent(event.target.value)} required />
            </label>
            <button type="submit" disabled={loading || !title.trim() || !content.trim()}>
              {loading ? messages.governance.importing : messages.governance.import}
            </button>
          </form>
        </AdminOnly>

        {message ? <p>{message}</p> : null}

        <section className="card stack">
          <h2>{messages.governance.documents}</h2>
          {documents.length === 0 ? <p>{messages.governance.noDocuments}</p> : null}
          {documents.map((document) => (
            <article key={document.id} className="stack">
              <h3>{document.title}</h3>
              <p>
                {document.document_type} · {document.scope} · {document.status}
              </p>
              {document.source_path ? (
                <p>
                  <strong>{messages.governance.source}:</strong> {document.source_path}
                </p>
              ) : null}
            </article>
          ))}
        </section>

        <section className="card stack">
          <h2>{messages.governance.drafts}</h2>
          {pendingRules.length === 0 ? <p>{messages.governance.noDrafts}</p> : null}
          {pendingRules.map((rule) => (
            <RuleCard
              key={rule.id}
              rule={rule}
              reviewingId={reviewingId}
              onReview={handleReview}
              canReview
            />
          ))}
        </section>

        <section className="card stack">
          <h2>{messages.governance.acceptedRules}</h2>
          {acceptedRules.map((rule) => (
            <RuleCard key={rule.id} rule={rule} reviewingId={reviewingId} onReview={handleReview} canReview={false} />
          ))}
        </section>
      </div>
    </main>
  );
}

function RuleCard({
  rule,
  reviewingId,
  onReview,
  canReview,
}: {
  rule: GovernanceRule;
  reviewingId: number | null;
  onReview: (ruleId: number, reviewState: "accepted" | "rejected") => Promise<void>;
  canReview: boolean;
}) {
  const { messages } = useI18n();
  const reviewing = reviewingId === rule.id;
  return (
    <article className="stack">
      <h3>{rule.title}</h3>
      <p>{rule.description}</p>
      <p>
        <strong>{messages.governance.severity}:</strong> {rule.severity} ·{" "}
        <strong>{messages.governance.scope}:</strong> {rule.scope} ·{" "}
        <strong>{messages.governance.status}:</strong> {rule.review_state}
      </p>
      {rule.rationale ? (
        <p>
          <strong>{messages.governance.rationale}:</strong> {rule.rationale}
        </p>
      ) : null}
      <p>
        <strong>{messages.governance.source}:</strong> {rule.source_title ?? `Document ${rule.document_id}`}
      </p>
      <details>
        <summary>{messages.governance.excerpt}</summary>
        <pre>{rule.source_excerpt}</pre>
      </details>
      {canReview ? (
        <ReviewOnly>
          <div className="action-row">
            <button type="button" disabled={reviewing} onClick={() => onReview(rule.id, "accepted")}>
              {reviewing ? messages.governance.reviewing : messages.governance.accept}
            </button>
            <button type="button" disabled={reviewing} onClick={() => onReview(rule.id, "rejected")}>
              {reviewing ? messages.governance.reviewing : messages.governance.reject}
            </button>
          </div>
        </ReviewOnly>
      ) : null}
    </article>
  );
}
