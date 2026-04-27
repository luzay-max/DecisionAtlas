"use client";

import Link from "next/link";
import React, { useState } from "react";

import { useProductSession } from "./session-provider";

export function AccountScopeSurface() {
  const { session, status, error, switchScope } = useProductSession();
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

  return (
    <div className="account-scope-surface" aria-label="Current account and owner scope">
      <div>
        <strong>{session.actor.username}</strong>
        {session.actor.bootstrap ? <span className="badge compact-badge">local bootstrap</span> : null}
      </div>
      <div className="muted">
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
      {switchError ? <p className="guided-demo-status">{switchError}</p> : null}
    </div>
  );
}
