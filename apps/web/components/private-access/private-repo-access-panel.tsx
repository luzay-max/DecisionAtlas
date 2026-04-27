"use client";

import Link from "next/link";
import React, { useState } from "react";

import { bindGithubPrivateAccess, type ImportLookup } from "../../lib/api";
import { AdminOnly } from "../auth/role-gate";
import { useProductSession } from "../auth/session-provider";

export function PrivateRepoAccessPanel() {
  return (
    <AdminOnly fallback="Admin role required for private repository access setup.">
      <PrivateRepoAccessForm />
    </AdminOnly>
  );
}

function PrivateRepoAccessForm() {
  const { session } = useProductSession();
  const [repo, setRepo] = useState("");
  const [token, setToken] = useState("");
  const [sourceRef, setSourceRef] = useState("");
  const [sourceLabel, setSourceLabel] = useState("");
  const [result, setResult] = useState<ImportLookup | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("Binding private repository access...");
    setResult(null);
    try {
      const trimmedRepo = repo.trim();
      const binding = await bindGithubPrivateAccess({
        repo: trimmedRepo,
        token: token.trim(),
        ...(sourceRef.trim() ? { source_ref: sourceRef.trim() } : { source_ref: trimmedRepo }),
        ...(sourceLabel.trim() ? { source_label: sourceLabel.trim() } : {}),
      });
      setResult(binding);
      setToken("");
      setMessage("Private repository access bound to this owner scope.");
    } catch (error) {
      setToken("");
      setMessage(error instanceof Error ? error.message : "Failed to bind private repository access");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card stack github-app-panel">
      <div>
        <p className="eyebrow">Private repo access</p>
        <h3>Bind token-backed repository access</h3>
        <p className="guided-demo-status">
          Current owner scope: <strong>{session?.current_owner_scope ?? "recovering session"}</strong>
        </p>
        <p>
          Use this admin setup path for private repositories that are not yet covered by a GitHub App installation.
          Tokens are submitted once and are not shown after binding.
        </p>
      </div>
      <form className="stack" onSubmit={handleSubmit}>
        <label className="field" htmlFor="private-access-repo">
          <span>Private repository</span>
          <input
            id="private-access-repo"
            type="text"
            value={repo}
            onChange={(event) => setRepo(event.target.value)}
            placeholder="owner/private-repo"
          />
        </label>
        <label className="field" htmlFor="private-access-token">
          <span>GitHub token</span>
          <input
            id="private-access-token"
            type="password"
            value={token}
            onChange={(event) => setToken(event.target.value)}
            placeholder="ghp_..."
            autoComplete="off"
          />
        </label>
        <div className="kpi-strip">
          <label className="field" htmlFor="private-access-source-ref">
            <span>Source reference</span>
            <input
              id="private-access-source-ref"
              type="text"
              value={sourceRef}
              onChange={(event) => setSourceRef(event.target.value)}
              placeholder="defaults to repository"
            />
          </label>
          <label className="field" htmlFor="private-access-source-label">
            <span>Source label</span>
            <input
              id="private-access-source-label"
              type="text"
              value={sourceLabel}
              onChange={(event) => setSourceLabel(event.target.value)}
              placeholder="team private repo"
            />
          </label>
        </div>
        <button type="submit" disabled={loading || repo.trim().length < 3 || token.trim().length === 0}>
          {loading ? "Binding private access..." : "Bind private repository access"}
        </button>
      </form>
      {message ? <p>{message}</p> : null}
      {result?.workspace_slug ? (
        <div className="card stack">
          <p>
            <strong>{result.access_source_label ?? "Private GitHub source"}</strong>
          </p>
          <p>
            Workspace <strong>{result.workspace_slug}</strong> is now private-access-backed for {result.repo}.
          </p>
          {result.access_source_status ? (
            <p>
              Authorization status:{" "}
              <strong>{result.access_source_status}</strong>
              {result.access_source_status_detail ? ` - ${result.access_source_status_detail}` : ""}
            </p>
          ) : null}
          <div className="action-row">
            <Link href={`/workspaces/${encodeURIComponent(result.workspace_slug)}`} className="action-link">
              Open workspace
            </Link>
            {result.can_incremental_sync ? (
              <Link href={`/workspaces/${encodeURIComponent(result.workspace_slug)}`} className="action-link">
                Review sync state
              </Link>
            ) : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
