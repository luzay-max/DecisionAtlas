"use client";

import Link from "next/link";
import React from "react";

export function WorkspaceContextBanner({
  workspaceSlug,
  current,
  description,
}: {
  workspaceSlug: string;
  current: string;
  description?: string;
}) {
  const encodedWorkspace = encodeURIComponent(workspaceSlug);

  return (
    <section className="workspace-context-banner" aria-label="Active workspace context">
      <div>
        <p className="eyebrow">Active workspace</p>
        <p className="workspace-context-title">{workspaceSlug}</p>
        <p className="muted">
          {current}
          {description ? ` · ${description}` : ""}
        </p>
      </div>
      <div className="action-row">
        <Link href={`/workspaces/${encodedWorkspace}`} className="action-link action-link-primary">
          Back to dashboard
        </Link>
        <Link href={`/review?workspace=${encodedWorkspace}`} className="action-link">
          Review
        </Link>
        <Link href={`/search?workspace=${encodedWorkspace}`} className="action-link">
          Why Search
        </Link>
        <Link href={`/timeline?workspace=${encodedWorkspace}`} className="action-link">
          Timeline
        </Link>
        <Link href={`/drift?workspace=${encodedWorkspace}`} className="action-link">
          Drift
        </Link>
      </div>
    </section>
  );
}
