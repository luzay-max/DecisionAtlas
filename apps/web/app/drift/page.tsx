import React from "react";

import { DriftAlertItem, getDriftAlerts } from "../../lib/api";
import { AlertDetail } from "../../components/drift/alert-detail";

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
          <AlertDetail key={alert.id} alert={alert} />
        ))}
      </section>
    </main>
  );
}

export default async function DriftPage() {
  const alerts = await getDriftAlerts("demo-workspace");
  return <DriftPageContent alerts={alerts} />;
}
