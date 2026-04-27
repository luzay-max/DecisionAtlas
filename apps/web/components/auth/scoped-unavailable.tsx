import Link from "next/link";
import React from "react";

export function ScopedUnavailable({
  workspaceSlug,
  message,
}: {
  workspaceSlug: string;
  message: string;
}) {
  return (
    <main className="page-shell">
      <section className="panel stack">
        <p className="eyebrow">Workspace unavailable in current scope</p>
        <h1>{workspaceSlug}</h1>
        <p>
          This workspace is not available in the current owner scope, or your current role cannot view it. Switch scope
          from the account panel if you have another owner scope.
        </p>
        <p className="guided-demo-status">{message}</p>
        <div className="action-row">
          <Link href="/" className="action-link">
            Back to home
          </Link>
          <Link href="/workspaces/demo-workspace" className="action-link">
            Open guided demo
          </Link>
        </div>
      </section>
    </main>
  );
}
