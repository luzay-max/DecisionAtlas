## Context

Public repository preflight currently relies on GitHub repository metadata. Any HTTP status error is converted to credential_required, so rate-limited shared CI runners can report a known public repository as private. The import itself already retries transport and selected 5xx responses, but preflight needs an independent public signal.

## Goals / Non-Goals

**Goals:**
- Verify public reachability without consuming repository metadata API quota.
- Preserve explicit private/not-found outcomes and provider/network categories.
- Keep fallback bounded, read-only, and unauthenticated.
- Make the real-repository Playwright path resilient on shared runners.

**Non-Goals:**
- Bypass private repository authorization.
- Hide persistent GitHub outages.
- Add shell git subprocesses or new dependencies.
- Retry malformed repository input.

## Decisions

### Use Git smart-HTTP info/refs as fallback

When metadata lookup fails for a public access source, the client probes the repository Git smart-HTTP info/refs endpoint with service=git-upload-pack. A 200 proves anonymous clone reachability; 401/403/404 does not.

Alternative: invoke git ls-remote. Rejected because it adds subprocess availability, timeout, and output parsing concerns.

### Keep metadata authoritative when available

A successful metadata response still determines the private flag and default branch. The fallback only proves public reachability and allows job creation; the normal importer later resolves branch metadata.

### Classify failed fallback using the original status

If metadata returns 404 and the public probe also fails, report credential_required. If metadata returns 403/429/5xx and the fallback cannot prove reachability, report network_failure rather than telling the user to add credentials.

## Risks / Trade-offs

- [Git endpoint also has a transient outage] -> Use existing bounded transport retries and return network_failure.
- [Private repository endpoint obscures existence] -> A failed probe never authorizes access.
- [Fallback passes but later API calls remain rate-limited] -> Import retains bounded provider retries and exposes operational failure honestly.

## Migration Plan

No database migration. Deploy client and preflight together; rollback removes the fallback and restores metadata-only behavior.
