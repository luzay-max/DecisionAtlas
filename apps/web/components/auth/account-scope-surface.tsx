"use client";

import Link from "next/link";
import React, { useState } from "react";

import { useProductSession } from "./session-provider";

export function AccountScopeSurface({ compact = false }: { compact?: boolean } = {}) {
  const { session, status, error, switchScope, logout } = useProductSession();
  const [switching, setSwitching] = useState(false);
  const [switchError, setSwitchError] = useState<string | null>(null);

  async function handleScopeChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const ownerScope = event.target.value;
    if (!ownerScope || ownerScope === session?.current_owner_scope) {
      return;
    }
    setSwitching(true);
    setSwitchError(null);
    try {
      await switchScope(ownerScope);
    } catch (scopeError) {
      setSwitchError(scopeError instanceof Error ? scopeError.message : "Scope switch failed");
    } finally {
      setSwitching(false);
    }
  }

  if (status === "loading") {
    return <div className="account-scope-surface muted">Recovering session...</div>;
  }

  if (!session) {
    return (
      <div className="account-scope-surface">
        <span>{error ?? "Login required"}</span>
        <Link href="/login" className="action-link">
          Login
        </Link>
      </div>
    );
  }

  const currentMembership =
    session.available_scopes.find((scope) => scope.owner_scope === session.current_owner_scope) ?? null;

  const accountDetails = (
    <>
      <div className="account-scope-identity">
        <strong>{session.actor.username}</strong>
        {session.actor.bootstrap ? <span className="badge compact-badge">local bootstrap</span> : null}
      </div>
      <div className="muted account-scope-metadata">
        Role: {currentMembership?.role ?? session.role} · Scope: {session.current_owner_scope}
      </div>
      {session.available_scopes.length > 1 ? (
        <label className="scope-switcher">
          <span>Switch scope</span>
          <select value={session.current_owner_scope} onChange={handleScopeChange} disabled={switching}>
            {session.available_scopes.map((scope) => (
              <option key={scope.owner_scope} value={scope.owner_scope}>
                {scope.owner_scope} ({scope.role})
              </option>
            ))}
          </select>
        </label>
      ) : null}
      <button type="button" onClick={() => void logout()} aria-label="Sign out">Sign out</button>
      {switchError ? <p className="guided-demo-status">{switchError}</p> : null}
    </>
  );

  if (compact) {
    return (
      <details className="account-scope-surface account-scope-compact" aria-label="Current account and owner scope">
        <summary className="account-scope-trigger">
          <span className="account-scope-avatar" aria-hidden="true">
            {session.actor.username.slice(0, 1).toUpperCase()}
          </span>
          <span className="account-scope-trigger-name">{session.actor.username}</span>
          <span className="account-scope-chevron" aria-hidden="true">⌄</span>
        </summary>
        <div className="account-scope-popover">{accountDetails}</div>
      </details>
    );
  }

  return (
    <div className="account-scope-surface" aria-label="Current account and owner scope">
      {accountDetails}
    </div>
  );
}
