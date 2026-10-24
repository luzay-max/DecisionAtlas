# Operator-only public evidence snapshot export

**State:** Experimental Phase A, local/offline. This tool exports database-stored candidate text and source snippets; it **does not fetch GitHub, verify actual upstream origins, validate PR merge state, run an LLM or act as a human reviewer**.

From the repo root, after independently reviewing that a **local SQLite DB contains only publishable public material**, use an existing SQLite database created from a public GitHub import:

```sh
uv run --project services/engine python scripts/eval/export_workspace_evidence.py \
  --sqlite /absolute/path/to/local-public.db \
  --workspace public-project-slug \
  --provider-kind unknown \
  --output /absolute/path/outside/checkout/public-evidence.json \
  --approve-public-data
```

On Windows PowerShell, put these arguments on a single line or use PowerShell continuation. `--provider-kind fake` is permitted only when the operator **knows** the candidates were extracted by FakeProvider. The database itself does not record reliable extraction-provider provenance, so `unknown` is safer by default. A `live` claim is intentionally unsupported at this stage.

The database is opened using SQLite URI `mode=ro` and `query_only`, and the output is created exclusively once. Destination must already have an existing parent directory, must not exist, and must be **outside this Git repository**. No database migrations, writes, credentials or network/API requests are performed. Exit `0` means export completed, **not** evidence quality approved; errors exit nonzero.

The JSON contains the exact stored `Decision.problem/chosen_option/tradeoffs`, stored review state, `SourceRef.quote/span`, `Artifact.content` and its UTF-8 SHA-256, original source URL and a copy of the offline diagnostic findings. Field `merged` is `null` because current GitHub PR import metadata stores a PR `state` but does not provide trustworthy merged status; fixed blob revision (if encoded in the URL) proves only URL syntax. All exports say `source_authenticity=remote_not_verified`, `human_review=not_run`, `model_accuracy=not_evaluated` and every diagnostic retains `review_required=true`.

The exporter **rejects** nonpublic/bound-access workspaces (including stale access-source bindings), mismatched workspace/artifact repository identities, cross-workspace SourceRef references, disagreeing SourceRef/Artifact URLs, source URLs outside the configured repository, malformed/credentialed/query-string URLs and destination paths inside the checkout. This is not a privacy classifier: even data labeled public can contain secrets or personal information. **Do not publish real exports or attach them to public CI/artifacts without an independent content review.**

Next: use this input for independent GitHub snapshot verification, then separate human sign-off and Why-search evaluation. See [execution plan](../plans/2026-10-24-evidence-verification-implementation-plan.md).
