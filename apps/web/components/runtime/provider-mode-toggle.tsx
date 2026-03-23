"use client";

import React, { useEffect, useState } from "react";

import { getProviderMode, ProviderModeState, setProviderMode } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function ProviderModeToggle() {
  const { messages } = useI18n();
  const [state, setState] = useState<ProviderModeState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const result = await getProviderMode();
        if (!cancelled) {
          setState(result);
        }
      } catch {
        if (!cancelled) {
          setError(messages.providerToggle.loadFailed);
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [messages.providerToggle.loadFailed]);

  async function handleSwitch(mode: "fake" | "live") {
    setLoading(true);
    setError(null);
    try {
      const result = await setProviderMode(mode);
      setState(result);
    } catch {
      setError(messages.providerToggle.updateFailed);
    } finally {
      setLoading(false);
    }
  }

  const currentMode = state?.is_live ? "live" : "fake";

  return (
    <div className="stack">
      <div className="action-row" aria-label={messages.providerToggle.label}>
        <button type="button" disabled={loading || currentMode === "fake"} onClick={() => handleSwitch("fake")}>
          {messages.providerToggle.fake}
        </button>
        <button type="button" disabled={loading || currentMode === "live"} onClick={() => handleSwitch("live")}>
          {messages.providerToggle.live}
        </button>
      </div>
      <p>
        {messages.providerToggle.current}:{" "}
        {currentMode === "live" ? messages.providerToggle.liveActive : messages.providerToggle.fakeActive}
      </p>
      {error ? <p>{error}</p> : null}
    </div>
  );
}
