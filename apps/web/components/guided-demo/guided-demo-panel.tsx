"use client";

import Link from "next/link";
import React from "react";

type GuidedDemoPanelProps = {
  step: number;
  total: number;
  title: string;
  description: string;
  steps: readonly string[];
  status?: string | null;
  nextHref?: string;
  nextLabel?: string;
  tone?: "default" | "success" | "warning";
  children?: React.ReactNode;
};

export function GuidedDemoPanel({
  step,
  total,
  title,
  description,
  steps,
  status,
  nextHref,
  nextLabel,
  tone = "default",
  children,
}: GuidedDemoPanelProps) {
  return (
    <section className={`card stack guided-demo-panel guided-demo-panel-${tone}`}>
      <div className="card-head">
        <div>
          <p className="eyebrow">Guided Demo</p>
          <h2>{title}</h2>
        </div>
        <span className="badge">
          Step {step} / {total}
        </span>
      </div>
      <p>{description}</p>
      <ol className="guided-demo-step-list">
        {steps.map((label, index) => {
          const stepNumber = index + 1;
          const className =
            stepNumber < step ? "guided-demo-step completed" : stepNumber === step ? "guided-demo-step active" : "guided-demo-step";
          return (
            <li key={label} className={className}>
              <span className="guided-demo-step-index">{stepNumber}</span>
              <span>{label}</span>
            </li>
          );
        })}
      </ol>
      {status ? <p className="guided-demo-status">{status}</p> : null}
      {children}
      {nextHref && nextLabel ? (
        <div className="action-row">
          <Link href={nextHref} className="action-link action-link-primary">
            {nextLabel}
          </Link>
        </div>
      ) : null}
    </section>
  );
}
