import React from "react";

import { DriftAlertItem } from "../../lib/api";
import { AlertDetail } from "./alert-detail";

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
        {alerts.length === 0 ? (
          <p>No drift alerts yet. Run the demo import, accept at least one decision, then re-check this page.</p>
        ) : null}
        {alerts.map((alert) => (
          <AlertDetail key={alert.id} alert={alert} />
        ))}
      </section>
    </main>
  );
}
