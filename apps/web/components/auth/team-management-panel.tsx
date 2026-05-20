"use client";

import React, { FormEvent, useEffect, useState } from "react";

import {
  ApiError,
  ProductRole,
  TeamAccount,
  WorkspaceMember,
  assignWorkspaceMember,
  createTeamAccount,
  disableTeamAccount,
  listTeamAccounts,
  listWorkspaceMembers,
  removeWorkspaceMember,
  resetTeamAccountPassword,
  updateTeamAccountRole,
} from "../../lib/api";
import { AdminOnly } from "./role-gate";
import { useProductSession } from "./session-provider";

type Role = "viewer" | "reviewer" | "admin";

const roles: Role[] = ["viewer", "reviewer", "admin"];

function roleLabel(role: ProductRole | null) {
  if (role === "admin") {
    return "Admin: manage imports, tokens, accounts, and workspace membership.";
  }
  if (role === "reviewer") {
    return "Reviewer: review decisions and governance rules, without account or token management.";
  }
  return "Viewer: read decisions, search, timeline, drift status, and evidence only.";
}

export function TeamManagementPanel() {
  const { session } = useProductSession();
  const [accounts, setAccounts] = useState<TeamAccount[]>([]);
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [workspaceSlug, setWorkspaceSlug] = useState("demo-workspace");
  const [status, setStatus] = useState("Load team accounts to start.");
  const [form, setForm] = useState({ username: "", displayName: "", password: "", role: "viewer" as Role });
  const [assignment, setAssignment] = useState({ actorId: "", role: "viewer" as Role });
  const [reset, setReset] = useState({ actorId: "", password: "" });

  async function refreshAccounts() {
    try {
      setAccounts(await listTeamAccounts());
      setStatus("Team accounts loaded.");
    } catch (error) {
      setStatus(error instanceof ApiError ? error.message : "Failed to load team accounts.");
    }
  }

  async function refreshMembers(slug = workspaceSlug) {
    try {
      setMembers(await listWorkspaceMembers(slug));
      setStatus(`Workspace members loaded for ${slug}.`);
    } catch (error) {
      setMembers([]);
      setStatus(error instanceof ApiError ? error.message : "Failed to load workspace members.");
    }
  }

  useEffect(() => {
    void refreshAccounts();
  }, []);

  async function submitAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await createTeamAccount({
        username: form.username,
        password: form.password,
        display_name: form.displayName || undefined,
        role: form.role,
      });
      setForm({ username: "", displayName: "", password: "", role: "viewer" });
      setStatus("Team account created.");
      await refreshAccounts();
    } catch (error) {
      setStatus(error instanceof ApiError ? error.message : "Failed to create account.");
    }
  }

  async function submitReset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await resetTeamAccountPassword(Number(reset.actorId), reset.password);
      setReset({ actorId: "", password: "" });
      setStatus("Password reset completed.");
    } catch (error) {
      setStatus(error instanceof ApiError ? error.message : "Failed to reset password.");
    }
  }

  async function submitAssignment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await assignWorkspaceMember(workspaceSlug, Number(assignment.actorId), assignment.role);
      setAssignment({ actorId: "", role: "viewer" });
      await refreshMembers();
      setStatus("Workspace member assignment updated.");
    } catch (error) {
      setStatus(error instanceof ApiError ? error.message : "Failed to assign workspace member.");
    }
  }

  return (
    <AdminOnly fallback="Admin role required for team account and workspace permission management.">
      <section className="stack">
        <div className="card">
          <p className="eyebrow">Team control plane</p>
          <h1>Accounts and workspace permissions</h1>
          <p className="lede">
            Current actor: {session?.actor.username ?? "unknown"} · Scope: {session?.current_owner_scope ?? "unknown"}
          </p>
          <p className="guided-demo-status">{status}</p>
        </div>

        <form className="card stack" onSubmit={submitAccount}>
          <h2>Create account</h2>
          <label className="field">
            Username
            <input value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} />
          </label>
          <label className="field">
            Display name
            <input value={form.displayName} onChange={(event) => setForm({ ...form, displayName: event.target.value })} />
          </label>
          <label className="field">
            Initial password
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
            />
          </label>
          <label className="field">
            Scope role
            <select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value as Role })}>
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </label>
          <p className="guided-demo-status">{roleLabel(form.role)}</p>
          <div className="action-row">
            <button type="submit">Create account</button>
            <button type="button" onClick={() => void refreshAccounts()}>
              Reload
            </button>
          </div>
        </form>

        <section className="card stack">
          <h2>Team accounts</h2>
          {accounts.map((account) => (
            <div className="card" key={account.id}>
              <div className="card-head">
                <div>
                  <strong>
                    #{account.id} {account.username}
                  </strong>
                  <p className="guided-demo-status">
                    {account.display_name ?? "No display name"} · {account.status} · {account.role}
                    {account.bootstrap ? " · bootstrap" : ""}
                  </p>
                  <p className="guided-demo-status">{roleLabel(account.role)}</p>
                </div>
                <div className="action-row">
                  <select
                    aria-label={`Role for ${account.username}`}
                    value={(account.role ?? "viewer") as Role}
                    onChange={(event) =>
                      void updateTeamAccountRole(account.id, event.target.value as Role).then(refreshAccounts)
                    }
                  >
                    {roles.map((role) => (
                      <option key={role} value={role}>
                        {role}
                      </option>
                    ))}
                  </select>
                  <button type="button" onClick={() => void disableTeamAccount(account.id).then(refreshAccounts)}>
                    Disable
                  </button>
                </div>
              </div>
            </div>
          ))}
        </section>

        <form className="card stack" onSubmit={submitReset}>
          <h2>Reset password</h2>
          <label className="field">
            Actor ID
            <input value={reset.actorId} onChange={(event) => setReset({ ...reset, actorId: event.target.value })} />
          </label>
          <label className="field">
            New password
            <input
              type="password"
              value={reset.password}
              onChange={(event) => setReset({ ...reset, password: event.target.value })}
            />
          </label>
          <button type="submit">Reset password</button>
        </form>

        <section className="card stack">
          <h2>Workspace members</h2>
          <label className="field">
            Workspace slug
            <input value={workspaceSlug} onChange={(event) => setWorkspaceSlug(event.target.value)} />
          </label>
          <div className="action-row">
            <button type="button" onClick={() => void refreshMembers()}>
              Load members
            </button>
          </div>
          <form className="stack" onSubmit={submitAssignment}>
            <label className="field">
              Actor ID
              <input
                value={assignment.actorId}
                onChange={(event) => setAssignment({ ...assignment, actorId: event.target.value })}
              />
            </label>
            <label className="field">
              Workspace role
              <select
                value={assignment.role}
                onChange={(event) => setAssignment({ ...assignment, role: event.target.value as Role })}
              >
                {roles.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
            </label>
            <p className="guided-demo-status">{roleLabel(assignment.role)}</p>
            <button type="submit">Assign member</button>
          </form>
          {members.map((member) => (
            <div className="card" key={`${member.workspace_id}-${member.actor.id}`}>
              <div className="card-head">
                <div>
                  <strong>
                    #{member.actor.id} {member.actor.username}
                  </strong>
                  <p className="guided-demo-status">{member.role} on this workspace</p>
                </div>
                <button
                  type="button"
                  onClick={() => void removeWorkspaceMember(workspaceSlug, member.actor.id).then(() => refreshMembers())}
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </section>
      </section>
    </AdminOnly>
  );
}
