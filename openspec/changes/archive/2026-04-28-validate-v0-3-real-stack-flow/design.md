## Context

The v0.3 RC baseline now documents the current product boundary and has passed the canonical `scripts/ci/pre-release.ps1` gate. That gate is necessary but not sufficient for planning the next development phase, because it does not produce a structured record of how the full local real stack, platform access flows, and operator-guided checks behave together.

The next change should therefore validate, not expand, the v0.3 product surface. The main output is an evidence report that separates blocking failures from known limitations and provider-dependent checks.

## Goals / Non-Goals

**Goals:**

- Produce a reproducible v0.3 real-stack validation report.
- Cover the demo lane, real Postgres/Redis stack, public import lane, auth/scope flows, GitHub App binding surface, private repo binding surface, hosted operator checks, and canonical release gate.
- Use existing scripts and product flows first; add small wrappers or docs only if the current commands are ambiguous or missing.
- Classify issues as `pass`, `blocking`, `non-blocking`, or `known limitation`.
- Preserve the distinction between mandatory offline release validation and optional live/provider-dependent validation.

**Non-Goals:**

- Do not add a new product feature under the label of validation.
- Do not require real private credentials, GitHub App production secrets, or network/provider-dependent checks in default CI.
- Do not build the next GitHub App webhook operations productization yet.
- Do not harden the private repo credential model beyond issues directly blocking the current validation matrix.
- Do not create or push a release tag.

## Decisions

1. Use a report-first validation model.

   Rationale: v0.3 has several product-visible paths with different dependency levels. A single pass/fail script would hide useful differences between local deterministic checks and operator-guided live checks. A structured report gives the next roadmap step a factual baseline.

   Alternative considered: add everything to `pre-release.ps1`. Rejected because live/provider-dependent checks would make the release gate flaky and harder to run locally.

2. Keep canonical release validation separate from real-stack confidence validation.

   Rationale: `pre-release.ps1` remains the release gate. The real-stack matrix is a broader confidence layer that can document manual or operator-observed outcomes without making them required for every release-style validation.

   Alternative considered: make real-stack validation required before every tag. Rejected until the product has stable hosted/test credentials and a fully deterministic environment.

3. Validate current flows before changing behavior.

   Rationale: the purpose is to discover whether the v0.3 RC baseline is coherent. Feature work belongs in follow-up changes such as GitHub App sync operations, private repo access hardening, real repo decision value quality, or hosted preview readiness.

   Alternative considered: combine validation with GitHub App sync productization. Rejected because it would blur baseline measurement with new capability development.

4. Treat missing observability as a validation finding.

   Rationale: if a product flow technically works but the user or operator cannot tell what happened, the report should capture that as a follow-up item rather than silently passing.

## Risks / Trade-offs

- Provider/network checks can be flaky -> keep them optional and record environment assumptions in the report.
- Real-stack startup can leave local services running -> include stop/cleanup commands and record whether cleanup was performed.
- Validation may uncover product bugs -> fix only blockers needed to make the current v0.3 baseline truthful; defer broader improvements to later changes.
- Manual observations can drift -> report commands, URLs, timestamps, and observed results so future maintainers can reproduce the judgment.
