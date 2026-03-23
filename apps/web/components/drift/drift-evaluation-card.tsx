"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

import { DriftEvaluation, evaluateDrift } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function DriftEvaluationCard({
  evaluation,
  workspaceSlug,
}: {
  evaluation: DriftEvaluation;
  workspaceSlug: string;
}) {
  const { messages } = useI18n();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleEvaluate() {
    setLoading(true);
    setError(null);
    try {
      await evaluateDrift(workspaceSlug);
      router.refresh();
    } catch {
      setError(messages.drift.evaluateFailed);
    } finally {
      setLoading(false);
    }
  }

  const title = messages.drift.states[evaluation.state as keyof typeof messages.drift.states] ?? evaluation.state;
  const detail =
    messages.drift.stateDetails[evaluation.state as keyof typeof messages.drift.stateDetails] ?? evaluation.state;

  return (
    <section className="card stack">
      <p className="eyebrow">{messages.drift.evaluationEyebrow}</p>
      <h2>{title}</h2>
      <p>{detail}</p>
      {evaluation.last_evaluated_at ? (
        <p>{messages.drift.lastEvaluated.replace("{timestamp}", evaluation.last_evaluated_at)}</p>
      ) : null}
      {evaluation.can_evaluate ? (
        <div className="action-row">
          <button type="button" onClick={() => void handleEvaluate()} disabled={loading}>
            {loading ? messages.drift.evaluating : messages.drift.evaluateNow}
          </button>
        </div>
      ) : null}
      {error ? <p>{error}</p> : null}
    </section>
  );
}
