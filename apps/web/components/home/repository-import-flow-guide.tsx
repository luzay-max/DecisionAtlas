"use client";

import Link from "next/link";
import React from "react";

export function RepositoryImportFlowGuide() {
  return (
    <section id="repository-import-flow" className="card import-flow-guide">
      <p className="eyebrow">Repository import flow</p>
      <h3>{"Connect source -> validate access -> import -> review"}</h3>
      <ol className="flow-steps" aria-label="Repository import steps">
        {["Connect source", "Validate access", "Import or reuse", "Open workspace"].map((step, index) => (
          <li key={step} className={index === 0 ? "active" : ""}>
            {step}
          </li>
        ))}
      </ol>
      <p className="muted">
        Use this guided path for public repositories, private token access, and existing workspace reuse. Admins can
        open advanced controls below to run the import.
      </p>
      <div className="action-row">
        <Link href="/#advanced-controls" className="action-link action-link-primary">
          Open import controls
        </Link>
        <Link href="/settings" className="action-link">
          Check providers
        </Link>
      </div>
    </section>
  );
}
