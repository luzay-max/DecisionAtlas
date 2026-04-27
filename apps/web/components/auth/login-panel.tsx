"use client";

import { useRouter, useSearchParams } from "next/navigation";
import React, { useState } from "react";

import { useProductSession } from "./session-provider";

export function LoginPanel() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, status, error } = useProductSession();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const next = searchParams.get("next") ?? "/";

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      await login(username, password);
      router.push(next);
    } catch {
      setMessage("Invalid username or password.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="panel stack login-panel">
      <div>
        <p className="eyebrow">DecisionAtlas login</p>
        <h1>Login required</h1>
        <p className="lede">Sign in before using imported workspace actions. Local bootstrap mode will recover automatically when enabled.</p>
      </div>
      {status === "unauthenticated" || error ? <p className="guided-demo-status">{error ?? "Authentication required"}</p> : null}
      <form className="stack" onSubmit={handleSubmit}>
        <label className="field" htmlFor="login-username">
          <span>Username</span>
          <input
            id="login-username"
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
          />
        </label>
        <label className="field" htmlFor="login-password">
          <span>Password</span>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
          />
        </label>
        <button type="submit" disabled={submitting || username.trim().length === 0 || password.length === 0}>
          {submitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
      {message ? <p>{message}</p> : null}
    </section>
  );
}
