"use client";

import Link from "next/link";
import React from "react";

import { useProductSession } from "../auth/session-provider";

function roleLabel(role: string | null | undefined) {
  if (role === "admin") return "Admin operator";
  if (role === "reviewer") return "Decision reviewer";
  if (role === "viewer") return "Read-only viewer";
  return "Local bootstrap or guest";
}

export function RoleAwareWorkbench() {
  const { session, status, canManageWorkspace, canReviewWorkspace } = useProductSession();
  const role = session?.role ?? null;
  const workspaceSlug = session?.available_scopes?.[0]?.owner_scope ?? "demo-workspace";
  const encodedWorkspace = encodeURIComponent(workspaceSlug);

  return (
    <section className="card role-workbench" aria-label="Role-aware next actions">
      <div>
        <p className="eyebrow">Role-aware workbench</p>
        <h2>Your fastest next step</h2>
        <p className="muted">
          {status === "unauthenticated"
            ? "Sign in to see admin, reviewer, viewer, or operator actions for your workspace."
            : `Current role: ${roleLabel(role)}. Start from the task that matches your responsibility.`}
        </p>
      </div>

      <div className="flow-grid">
        {canManageWorkspace ? (
          <div className="card flow-card">
            <p className="eyebrow">Admin</p>
            <h3>Connect and operate</h3>
            <p className="muted">Configure providers, connect repositories, manage members, and check release evidence.</p>
            <div className="action-row">
              <Link href="/#repository-import-flow" className="action-link action-link-primary">
                Import repository
              </Link>
              <Link href="/settings" className="action-link">
                Provider settings
              </Link>
              <Link href="/team" className="action-link">
                Team accounts
              </Link>
            </div>
          </div>
        ) : null}

        {canReviewWorkspace ? (
          <div className="card flow-card">
            <p className="eyebrow">Reviewer</p>
            <h3>Review decisions</h3>
            <p className="muted">Go directly to candidate decisions and continue reviewing with source evidence.</p>
            <div className="action-row">
              <Link href={`/review?workspace=${encodedWorkspace}`} className="action-link action-link-primary">
                Open review queue
              </Link>
              <Link href={`/workspaces/${encodedWorkspace}`} className="action-link">
                Workspace dashboard
              </Link>
            </div>
          </div>
        ) : null}

        <div className="card flow-card">
          <p className="eyebrow">Viewer</p>
          <h3>Discover decisions</h3>
          <p className="muted">Read decisions, ask why, inspect timeline, and check drift without management actions.</p>
          <div className="action-row">
            <Link href={`/search?workspace=${encodedWorkspace}`} className="action-link action-link-primary">
              Ask why
            </Link>
            <Link href={`/timeline?workspace=${encodedWorkspace}`} className="action-link">
              Timeline
            </Link>
            <Link href="/evidence" className="action-link">
              Evidence
            </Link>
          </div>
        </div>

        <div className="card flow-card">
          <p className="eyebrow">Operator</p>
          <h3>Release readiness</h3>
          <p className="muted">Check guardrails, benchmark comparison, hosted readiness, and missing evidence.</p>
          <div className="action-row">
            <Link href="/evidence" className="action-link action-link-primary">
              Evidence Center
            </Link>
            <Link href="/governance" className="action-link">
              Governance
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
