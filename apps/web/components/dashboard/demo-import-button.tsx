"use client";

import React, { useState } from "react";

import { startGithubImport } from "../../lib/api";

export function DemoImportButton({ workspaceSlug }: { workspaceSlug: string }) {
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    try {
      const response = await startGithubImport(workspaceSlug, "org/repo");
      setMessage(`Imported ${response.imported_count} artifacts`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <button type="button" onClick={handleClick}>
        {loading ? "Importing..." : "Run Demo Import"}
      </button>
      {message ? <p>{message}</p> : null}
    </div>
  );
}
