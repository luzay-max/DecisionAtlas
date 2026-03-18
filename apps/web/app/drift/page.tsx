import React from "react";

import { DriftAlertItem, getDriftAlerts } from "../../lib/api";

export function DriftPageContent({ alerts }: { alerts: DriftAlertItem[] }) {
  return (
    <main className="page-shell">
      <section className="panel stack">
        <div>
          <p className="eyebrow">Drift Alerts</p>
          <h1>Possible decision drift</h1>
          <p className="lede">
            Rule-first alerts stay conservative. Every item points back to the accepted decision and the triggering artifact.
          </p>
        </div>
        {alerts.length === 0 ? <p>No drift alerts yet.</p> : null}
        {alerts.map((alert) => (
          <article key={alert.id} className="card stack">
            <div className="card-head">
              <div>
                <strong>{alert.alert_type}</strong>
                <p>{alert.summary}</p>
              </div>
              <span className="badge">{alert.status}</span>
            </div>
            {alert.decision ? (
              <p>
                Decision: <strong>{alert.decision.title}</strong>
              </p>
            ) : null}
            {alert.artifact ? (
              <p>
                Artifact:{" "}
                {alert.artifact.url ? (
                  <a href={alert.artifact.url}>{alert.artifact.title ?? `Artifact ${alert.artifact.id}`}</a>
                ) : (
                  <strong>{alert.artifact.title ?? `Artifact ${alert.artifact.id}`}</strong>
                )}
              </p>
            ) : null}
          </article>
        ))}
      </section>
    </main>
  );
}

export default async function DriftPage() {
  const alerts = await getDriftAlerts("demo-workspace");
  return <DriftPageContent alerts={alerts} />;
}
