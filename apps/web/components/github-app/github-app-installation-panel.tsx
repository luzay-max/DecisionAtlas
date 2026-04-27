"use client";

import Link from "next/link";
import React, { useState } from "react";

import { bindGithubAppInstallation, type ImportLookup } from "../../lib/api";
import { AdminOnly } from "../auth/role-gate";
import { useProductSession } from "../auth/session-provider";

export function GitHubAppInstallationPanel() {
  return (
    <AdminOnly fallback="Admin role required for GitHub App installation setup.">
      <InstallationForm />
    </AdminOnly>
  );
}

function InstallationForm() {
  const { session } = useProductSession();
  const [repo, setRepo] = useState("");
  const [installationId, setInstallationId] = useState("");
  const [accountLogin, setAccountLogin] = useState("");
  const [accountType, setAccountType] = useState("");
  const [result, setResult] = useState<ImportLookup | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("Binding GitHub App installation...");
    setResult(null);
    try {
      const binding = await bindGithubAppInstallation({
        repo: repo.trim(),
        installation_id: installationId.trim(),
        ...(accountLogin.trim() ? { account_login: accountLogin.trim() } : {}),
        ...(accountType.trim() ? { account_type: accountType.trim() } : {}),
      });
      setResult(binding);
      setMessage("GitHub App installation bound to this owner scope.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to bind GitHub App installation");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card stack github-app-panel">
      <div>
        <p className="eyebrow">GitHub App setup</p>
        <h3>Bind repository to installation</h3>
        <p className="guided-demo-status">
          Current owner scope: <strong>{session?.current_owner_scope ?? "recovering session"}</strong>
        </p>
        <p>
          Use this admin setup path when a GitHub App installation already exists. Full GitHub callback automation is a
          follow-up slice.
        </p>
      </div>
      <form className="stack" onSubmit={handleSubmit}>
        <label className="field" htmlFor="github-app-repo">
          <span>Repository</span>
          <input
            id="github-app-repo"
            type="text"
            value={repo}
            onChange={(event) => setRepo(event.target.value)}
            placeholder="owner/repo"
          />
        </label>
        <label className="field" htmlFor="github-app-installation-id">
          <span>Installation ID</span>
          <input
            id="github-app-installation-id"
            type="text"
            value={installationId}
            onChange={(event) => setInstallationId(event.target.value)}
            placeholder="12345"
          />
        </label>
        <div className="kpi-strip">
          <label className="field" htmlFor="github-app-account-login">
            <span>Account login</span>
            <input
              id="github-app-account-login"
              type="text"
              value={accountLogin}
              onChange={(event) => setAccountLogin(event.target.value)}
              placeholder="org or user"
            />
          </label>
          <label className="field" htmlFor="github-app-account-type">
            <span>Account type</span>
            <input
              id="github-app-account-type"
              type="text"
              value={accountType}
              onChange={(event) => setAccountType(event.target.value)}
              placeholder="Organization"
            />
          </label>
        </div>
        <button type="submit" disabled={loading || repo.trim().length < 3 || installationId.trim().length === 0}>
          {loading ? "Binding installation..." : "Bind GitHub App installation"}
        </button>
      </form>
      {message ? <p>{message}</p> : null}
      {result?.workspace_slug ? (
        <div className="card stack">
          <p>
            <strong>{result.access_source_label ?? "GitHub App installation"}</strong>
          </p>
          <p>
            Workspace <strong>{result.workspace_slug}</strong> is now installation-backed for {result.repo}.
          </p>
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
