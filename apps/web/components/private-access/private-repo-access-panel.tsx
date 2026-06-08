"use client";

import Link from "next/link";
import React, { useState } from "react";

import { bindGitSource, type ImportLookup } from "../../lib/api";
import { accessSourceStatusLabel, privateAccessRecoveryCopy } from "../access-source/access-source-status";
import { AdminOnly } from "../auth/role-gate";
import { useProductSession } from "../auth/session-provider";
import { useI18n } from "../i18n/language-provider";

export function PrivateRepoAccessPanel() {
  return (
    <AdminOnly fallback="Admin role required for private repository access setup.">
      <PrivateRepoAccessForm />
    </AdminOnly>
  );
}

function PrivateRepoAccessForm() {
  const { messages } = useI18n();
  const { session } = useProductSession();
  const [provider, setProvider] = useState("github");
  const [accessMode, setAccessMode] = useState("token");
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
    setMessage("Binding Git source access...");
    setResult(null);
    try {
      const trimmedRepo = repo.trim();
      const binding = await bindGitSource({
        provider,
        access_mode: accessMode,
        repo: trimmedRepo,
        ...(accessMode === "token" ? { token: token.trim() } : {}),
        ...(sourceRef.trim() ? { source_ref: sourceRef.trim() } : { source_ref: trimmedRepo }),
        ...(sourceLabel.trim() ? { source_label: sourceLabel.trim() } : {}),
      });
      setResult(binding);
      setToken("");
      if (binding.setup_outcome === "provider_unsupported") {
        setMessage("This Git provider is recorded as operator-guided until its importer is implemented.");
      } else if (binding.setup_outcome === "local_path_unavailable") {
        setMessage("Local path import is recorded as server-operator-guided for this self-hosted instance.");
      } else {
        setMessage("Git source access bound to this owner scope.");
      }
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
          {messages.privateAccess.boundary}
        </p>
      </div>
      <form className="stack" onSubmit={handleSubmit}>
        <div className="kpi-strip">
          <label className="field" htmlFor="git-source-provider">
            <span>Git provider</span>
            <select
              id="git-source-provider"
              value={provider}
              onChange={(event) => {
                const nextProvider = event.target.value;
                setProvider(nextProvider);
                setAccessMode(nextProvider === "local" ? "local_path" : "token");
              }}
            >
              <option value="github">GitHub</option>
              <option value="gitlab">GitLab</option>
              <option value="gitee">Gitee</option>
              <option value="local">Local path</option>
            </select>
          </label>
          <label className="field" htmlFor="git-source-access-mode">
            <span>Access mode</span>
            <select
              id="git-source-access-mode"
              value={accessMode}
              onChange={(event) => setAccessMode(event.target.value)}
            >
              <option value="token">Token</option>
              <option value="public">Public</option>
              <option value="local_path">Local path</option>
            </select>
          </label>
        </div>
        <label className="field" htmlFor="private-access-repo">
          <span>{provider === "local" || accessMode === "local_path" ? "Server local path label" : "Repository"}</span>
          <input
            id="private-access-repo"
            type="text"
            value={repo}
            onChange={(event) => setRepo(event.target.value)}
            placeholder={provider === "local" || accessMode === "local_path" ? "server-local-repo" : "owner/private-repo"}
          />
        </label>
        {accessMode === "token" ? (
          <label className="field" htmlFor="private-access-token">
            <span>{provider === "github" ? "GitHub token" : "Provider token"}</span>
            <input
              id="private-access-token"
              type="password"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              placeholder={provider === "github" ? "ghp_..." : "token is stored only for supported providers"}
              autoComplete="off"
            />
          </label>
        ) : null}
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
        <button
          type="submit"
          disabled={loading || repo.trim().length < 3 || (accessMode === "token" && token.trim().length === 0)}
        >
          {loading ? "Binding Git source..." : "Bind Git source access"}
        </button>
      </form>
      {message ? <p>{message}</p> : null}
      {result?.workspace_slug ? (
        <div className="card stack">
          <p>
            <strong>{result.access_source_label ?? "Private GitHub source"}</strong>
          </p>
          <p>
            Provider <strong>{result.provider ?? "github"}</strong>, mode{" "}
            <strong>{result.access_mode ?? result.access_source_type ?? "unknown"}</strong>
            {result.setup_outcome ? (
              <>
                , outcome <strong>{result.setup_outcome}</strong>
              </>
            ) : null}
          </p>
          <p>
            Workspace <strong>{result.workspace_slug}</strong> is now private-access-backed for {result.repo}.
          </p>
          {result.access_source_status ? (
            <p>
              Authorization status:{" "}
              <strong>{accessSourceStatusLabel(messages, result.access_source_status)}</strong>
              {result.access_source_status_detail ? ` - ${result.access_source_status_detail}` : ""}
            </p>
          ) : null}
          {privateAccessRecoveryCopy(messages, result.access_source_status) ? (
            <p>{privateAccessRecoveryCopy(messages, result.access_source_status)}</p>
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
      {result && !result.workspace_slug ? (
        <div className="card stack">
          <p>
            <strong>{result.access_source_label ?? "Git source setup"}</strong>
          </p>
          <p>
            Provider <strong>{result.provider ?? provider}</strong>, mode{" "}
            <strong>{result.access_mode ?? accessMode}</strong>, outcome{" "}
            <strong>{result.setup_outcome ?? result.access_source_status ?? "recorded"}</strong>.
          </p>
          {result.next_action ? (
            <p>
              Next action: <strong>{result.next_action}</strong>
            </p>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
