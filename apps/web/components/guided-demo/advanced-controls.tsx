"use client";

import React from "react";

import { useI18n } from "../i18n/language-provider";

export function AdvancedControls({
  children,
  id,
}: {
  children: React.ReactNode;
  id?: string;
}) {
  const { messages } = useI18n();

  return (
    <details className="card advanced-controls" id={id}>
      <summary>{messages.advanced.summary}</summary>
      <div className="stack advanced-controls-body">
        <div>
          <p className="eyebrow">{messages.advanced.eyebrow}</p>
          <h2>{messages.advanced.title}</h2>
          <p>{messages.advanced.description}</p>
          <p>{messages.advanced.boundary}</p>
        </div>
        {children}
      </div>
    </details>
  );
}
