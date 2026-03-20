"use client";

import React from "react";

import { DriftAlertItem } from "../../lib/api";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { useI18n } from "../i18n/language-provider";
import { AlertDetail } from "./alert-detail";

export function DriftPageContent({ alerts, workspaceSlug }: { alerts: DriftAlertItem[]; workspaceSlug: string }) {
  const { messages } = useI18n();

  return (
    <main className="page-shell">
      <section className="panel stack">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/drift" />
        <div>
          <p className="eyebrow">{messages.drift.eyebrow}</p>
          <h1>{messages.drift.title}</h1>
          <p className="lede">{messages.drift.lede}</p>
        </div>
        {alerts.length === 0 ? (
          <p>{messages.drift.none}</p>
        ) : null}
        {alerts.map((alert) => (
          <AlertDetail key={alert.id} alert={alert} workspaceSlug={workspaceSlug} />
        ))}
      </section>
    </main>
  );
}
