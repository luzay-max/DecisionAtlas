import React from "react";

import { DriftAlertItem } from "../../lib/api";

export function AlertDetail({ alert }: { alert: DriftAlertItem }) {
  return (
    <article className="card stack">
      <div className="card-head">
        <div>
          <strong>{alert.alert_type}</strong>
          <p>{alert.summary}</p>
        </div>
        <div className="stack">
          <span className="badge">{alert.status}</span>
          <span className="badge">{alert.confidence_label} confidence</span>
        </div>
      </div>
      {alert.decision ? (
        <div className="stack">
          <p>
            Matched decision: <strong>{alert.decision.title}</strong>
          </p>
          <p>Chosen option: {alert.decision.chosen_option}</p>
        </div>
      ) : null}
      {alert.artifact ? (
        <p>
          Triggering artifact:{" "}
          {alert.artifact.url ? (
            <a href={alert.artifact.url}>{alert.artifact.title ?? `Artifact ${alert.artifact.id}`}</a>
          ) : (
            <strong>{alert.artifact.title ?? `Artifact ${alert.artifact.id}`}</strong>
          )}
        </p>
      ) : null}
    </article>
  );
}
