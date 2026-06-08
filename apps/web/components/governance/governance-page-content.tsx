"use client";

import React, { useState } from "react";

import {
  GovernanceDocument,
  GovernanceRule,
  importGovernanceDocument,
  reviewGovernanceRule,
  updateGovernanceRuleLifecycle,
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
  const [lifecycleUpdatingId, setLifecycleUpdatingId] = useState<number | null>(null);
  const [acceptedScopeFilter, setAcceptedScopeFilter] = useState("all");
  const [acceptedSeverityFilter, setAcceptedSeverityFilter] = useState("all");
  const [acceptedRuleTypeFilter, setAcceptedRuleTypeFilter] = useState("all");
  const [acceptedLifecycleFilter, setAcceptedLifecycleFilter] = useState("all");

  const pendingRules = rules.filter((rule) => rule.review_state === "pending");
  const acceptedRules = rules.filter((rule) => rule.review_state === "accepted");
  const filteredAcceptedRules = acceptedRules.filter((rule) => {
    return (
      (acceptedScopeFilter === "all" || rule.scope === acceptedScopeFilter) &&
      (acceptedSeverityFilter === "all" || rule.severity === acceptedSeverityFilter) &&
      (acceptedRuleTypeFilter === "all" || (rule.rule_type ?? "standard") === acceptedRuleTypeFilter) &&
      (acceptedLifecycleFilter === "all" || (rule.lifecycle_status ?? "current") === acceptedLifecycleFilter)
    );
  });
  const acceptedScopes = uniqueRuleValues(acceptedRules.map((rule) => rule.scope));
  const acceptedSeverities = uniqueRuleValues(acceptedRules.map((rule) => rule.severity));
  const acceptedRuleTypes = uniqueRuleValues(acceptedRules.map((rule) => rule.rule_type ?? "standard"));
  const acceptedLifecycleStatuses = uniqueRuleValues(acceptedRules.map((rule) => rule.lifecycle_status ?? "current"));

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

  async function handleReview(ruleId: number, reviewState: "accepted" | "rejected", reviewRationale?: string) {
    setReviewingId(ruleId);
    setMessage(null);
    try {
      const updatedRule = await reviewGovernanceRule(ruleId, reviewState, reviewRationale);
      setRules(rules.map((rule) => (rule.id === updatedRule.id ? updatedRule : rule)));
    } catch {
      setMessage(messages.governance.reviewFailed);
    } finally {
      setReviewingId(null);
    }
  }

  async function handleLifecycle(
    ruleId: number,
    lifecycleStatus: "stale" | "superseded",
    lifecycleRationale?: string,
    supersededByRuleId?: number
  ) {
    setLifecycleUpdatingId(ruleId);
    setMessage(null);
    try {
      const updatedRule = await updateGovernanceRuleLifecycle(
        ruleId,
        lifecycleStatus,
        lifecycleRationale,
        supersededByRuleId
      );
      setRules(rules.map((rule) => (rule.id === updatedRule.id ? updatedRule : rule)));
    } catch {
      setMessage(messages.governance.lifecycleFailed);
    } finally {
      setLifecycleUpdatingId(null);
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
              lifecycleUpdatingId={lifecycleUpdatingId}
            />
          ))}
        </section>

        <section className="card stack">
          <h2>{messages.governance.acceptedRules}</h2>
          <div className="grid two">
            <FilterSelect
              label={messages.governance.filterScope}
              value={acceptedScopeFilter}
              values={acceptedScopes}
              onChange={setAcceptedScopeFilter}
            />
            <FilterSelect
              label={messages.governance.filterSeverity}
              value={acceptedSeverityFilter}
              values={acceptedSeverities}
              onChange={setAcceptedSeverityFilter}
            />
            <FilterSelect
              label={messages.governance.filterRuleType}
              value={acceptedRuleTypeFilter}
              values={acceptedRuleTypes}
              onChange={setAcceptedRuleTypeFilter}
            />
            <FilterSelect
              label={messages.governance.filterLifecycle}
              value={acceptedLifecycleFilter}
              values={acceptedLifecycleStatuses}
              onChange={setAcceptedLifecycleFilter}
            />
          </div>
          {filteredAcceptedRules.length === 0 ? <p>{messages.governance.noAcceptedRules}</p> : null}
          {filteredAcceptedRules.map((rule) => {
            const replacementCandidates = acceptedRules.filter(
              (candidate) => candidate.id !== rule.id && (candidate.lifecycle_status ?? "current") === "current"
            );
            return (
              <RuleCard
                key={rule.id}
                rule={rule}
                reviewingId={reviewingId}
                lifecycleUpdatingId={lifecycleUpdatingId}
                onReview={handleReview}
                onLifecycle={handleLifecycle}
                replacementCandidates={replacementCandidates}
                canReview={false}
              />
            );
          })}
        </section>
      </div>
    </main>
  );
}

function RuleCard({
  rule,
  reviewingId,
  lifecycleUpdatingId,
  onReview,
  onLifecycle,
  replacementCandidates = [],
  canReview,
}: {
  rule: GovernanceRule;
  reviewingId: number | null;
  lifecycleUpdatingId?: number | null;
  onReview: (ruleId: number, reviewState: "accepted" | "rejected", reviewRationale?: string) => Promise<void>;
  onLifecycle?: (
    ruleId: number,
    lifecycleStatus: "stale" | "superseded",
    lifecycleRationale?: string,
    supersededByRuleId?: number
  ) => Promise<void>;
  replacementCandidates?: GovernanceRule[];
  canReview: boolean;
}) {
  const { messages } = useI18n();
  const [reviewRationale, setReviewRationale] = useState("");
  const [lifecycleRationale, setLifecycleRationale] = useState("");
  const [replacementRuleId, setReplacementRuleId] = useState("");
  const reviewing = reviewingId === rule.id;
  const lifecycleUpdating = lifecycleUpdatingId === rule.id;
  const canManageLifecycle =
    Boolean(onLifecycle) && rule.review_state === "accepted" && (rule.lifecycle_status ?? "current") === "current";
  const selectedReplacementId = replacementRuleId || String(replacementCandidates[0]?.id ?? "");
  return (
    <article className="stack">
      <h3>{rule.title}</h3>
      <p>{rule.description}</p>
      <p>
        <strong>{messages.governance.severity}:</strong> {rule.severity} ·{" "}
        <strong>{messages.governance.scope}:</strong> {rule.scope} ·{" "}
        <strong>{messages.governance.status}:</strong> {rule.review_state} ·{" "}
        <strong>{messages.governance.lifecycle}:</strong> {rule.lifecycle_status ?? "current"}
      </p>
      <p>
        <strong>{messages.governance.ruleType}:</strong> {rule.rule_type ?? "standard"} ·{" "}
        <strong>{messages.governance.extractionReason}:</strong> {rule.extraction_reason ?? messages.governance.notAvailable}
      </p>
      {rule.rationale ? (
        <p>
          <strong>{messages.governance.rationale}:</strong> {rule.rationale}
        </p>
      ) : null}
      {rule.review_rationale ? (
        <p>
          <strong>{messages.governance.reviewRationale}:</strong> {rule.review_rationale}
        </p>
      ) : null}
      {rule.lifecycle_rationale ? (
        <p>
          <strong>{messages.governance.lifecycleRationale}:</strong> {rule.lifecycle_rationale}
        </p>
      ) : null}
      {rule.superseded_by_rule_id ? (
        <p>
          <strong>{messages.governance.supersededBy}:</strong> #{rule.superseded_by_rule_id}
        </p>
      ) : null}
      <p>
        <strong>{messages.governance.source}:</strong> {rule.source_title ?? `Document ${rule.document_id}`}
      </p>
      <details>
        <summary>{messages.governance.excerpt}</summary>
        <pre>{rule.source_excerpt}</pre>
      </details>
      {rule.audit_history?.length ? (
        <section className="stack" aria-label="Governance rule audit history">
          <h4>Review history</h4>
          {rule.audit_history.map((event) => (
            <p key={event.id}>
              <strong>{event.actor_username}</strong> {event.action.replaceAll("_", " ")}
              {event.rationale ? `: ${event.rationale}` : ""}{" "}
              {event.created_at ? <span className="muted">{event.created_at}</span> : null}
            </p>
          ))}
        </section>
      ) : null}
      {canReview ? (
        <ReviewOnly>
          <label>
            <strong>{messages.governance.reviewRationale}</strong>
            <textarea
              rows={3}
              value={reviewRationale}
              onChange={(event) => setReviewRationale(event.target.value)}
            />
          </label>
          <div className="action-row">
            <button type="button" disabled={reviewing} onClick={() => onReview(rule.id, "accepted", reviewRationale)}>
              {reviewing ? messages.governance.reviewing : messages.governance.accept}
            </button>
            <button type="button" disabled={reviewing} onClick={() => onReview(rule.id, "rejected", reviewRationale)}>
              {reviewing ? messages.governance.reviewing : messages.governance.reject}
            </button>
          </div>
        </ReviewOnly>
      ) : null}
      {canManageLifecycle ? (
        <ReviewOnly>
          <div className="stack">
            <label>
              <strong>{messages.governance.lifecycleRationale}</strong>
              <textarea
                rows={3}
                value={lifecycleRationale}
                onChange={(event) => setLifecycleRationale(event.target.value)}
              />
            </label>
            <div className="action-row">
              <button
                type="button"
                disabled={lifecycleUpdating}
                onClick={() => onLifecycle?.(rule.id, "stale", lifecycleRationale)}
              >
                {lifecycleUpdating ? messages.governance.reviewing : messages.governance.markStale}
              </button>
            </div>
            <label>
              <strong>{messages.governance.replacementRule}</strong>
              <select value={selectedReplacementId} onChange={(event) => setReplacementRuleId(event.target.value)}>
                {replacementCandidates.length === 0 ? (
                  <option value="">{messages.governance.noReplacementRules}</option>
                ) : null}
                {replacementCandidates.map((candidate) => (
                  <option key={candidate.id} value={candidate.id}>
                    #{candidate.id} {candidate.title}
                  </option>
                ))}
              </select>
            </label>
            <div className="action-row">
              <button
                type="button"
                disabled={lifecycleUpdating || !selectedReplacementId}
                onClick={() =>
                  onLifecycle?.(rule.id, "superseded", lifecycleRationale, Number(selectedReplacementId))
                }
              >
                {lifecycleUpdating ? messages.governance.reviewing : messages.governance.markSuperseded}
              </button>
            </div>
          </div>
        </ReviewOnly>
      ) : null}
    </article>
  );
}

function FilterSelect({
  label,
  value,
  values,
  onChange,
}: {
  label: string;
  value: string;
  values: string[];
  onChange: (value: string) => void;
}) {
  const { messages } = useI18n();
  return (
    <label>
      <strong>{label}</strong>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="all">{messages.governance.allFilter}</option>
        {values.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>
    </label>
  );
}

function uniqueRuleValues(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean))).sort();
}
