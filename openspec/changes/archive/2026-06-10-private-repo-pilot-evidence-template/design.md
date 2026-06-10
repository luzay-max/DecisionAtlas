## Context

The current product can generate release evidence, hosted/operator readiness, readiness history, team handoff reports, package verification, clean install rehearsal evidence, and Code Decision Audit reports. Public repository validation is already repeatable, but private-repository proof is commercially more important and cannot be committed as raw evidence because it may include repository names, token setup details, private source snippets, issue/PR text, local paths, or customer identifiers.

The design must keep private-repo proof operator-local while still giving the maintainer a safe, reusable evidence shape for pilot claims. The workflow should integrate with existing delivery materials and verifiers instead of adding a new service, database table, hosted vault, or SaaS control plane.

## Goals / Non-Goals

**Goals:**

- Define a private-repo pilot evidence template with explicit redaction and custody boundaries.
- Provide a verifier that can validate JSON/Markdown evidence shape and required safety statements.
- Provide a safe operator-guided sample that can be committed without private content.
- Make pilot and self-hosted commercial materials point to the private-repo evidence workflow when private-repo proof is claimed.
- Keep warning, operator-guided, not-provided, and blocking states visible.

**Non-Goals:**

- Do not store or process private repository tokens in a new hosted secret vault.
- Do not commit raw private repository source, issue/PR text, screenshots containing private code, model raw output, or customer-specific identifiers.
- Do not add billing, SaaS tenancy, Marketplace OAuth, enterprise SSO, runtime license enforcement, or online license checks.
- Do not require a live private repository in default CI.

## Decisions

1. Private-repo evidence is a document/template plus verifier, not a new database model.

   Rationale: the high-value problem is safe proof capture and customer handoff, not runtime persistence. Existing evidence history and handoff flows already handle durable artifacts. A lightweight verifier is enough to prevent unsafe or incomplete pilot claims.

   Alternative considered: add a `private_repo_pilot_evidence` table and UI. Rejected because it expands product scope and still cannot safely commit customer-private proof.

2. The committed sample evidence remains `operator_guided`.

   Rationale: no committed artifact can prove a real private-repo run without either disclosing private data or relying on unverifiable claims. The safe sample demonstrates the shape and mandatory disclosures; actual proof stays customer-controlled or redacted.

   Alternative considered: generate a fake `pass` sample. Rejected because it would teach operators to overstate readiness.

3. The verifier checks safety contracts, not private-repo truth.

   Rationale: CI can verify that evidence contains redaction notes, token non-retention statements, status fields, required lanes, and no obvious forbidden tokens. CI cannot verify a customer's private repository was actually imported unless the operator supplies local evidence.

   Alternative considered: require live GitHub private repo credentials in CI. Rejected for security and repeatability.

4. Existing pilot and self-hosted package verifiers should include the new template as required customer-facing material.

   Rationale: private-repo evidence is now part of the commercial pilot path. Including it in the package and pilot kit prevents the workflow from becoming tribal knowledge.

## Risks / Trade-offs

- Private proof can be overstated by humans -> The template requires explicit status, limitation, and source-custody fields; verifier preserves non-pass states.
- Redacted summaries may be too thin for a customer -> The template asks for counts, state transitions, review outcomes, why/drift usefulness, and operator notes without raw content.
- Verifier may miss a sensitive string -> The script uses bounded heuristics and required declarations, but still states that operator review is required before sharing.
- More documents can confuse pilots -> The pilot kit links the template only when private-repo proof is part of the claim, keeping public/demo pilots simpler.
