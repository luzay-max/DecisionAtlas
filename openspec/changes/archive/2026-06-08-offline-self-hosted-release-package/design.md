## Context

DecisionAtlas already has real-stack startup scripts, release/readiness evidence collectors, self-hosted checklists, and team workflow rehearsals. Those pieces are useful for maintainers, but a self-hosted buyer or pilot operator still needs a bounded release-package handoff: what files are included, what commands to run, how to verify the package, and how to recover or upgrade without relying on undocumented maintainer knowledge.

The package should remain source-tree based for this stage. A fully compiled installer, container registry publishing flow, license enforcement system, or managed SaaS control plane would be premature and would conflict with the current self-hosted-first strategy.

## Goals / Non-Goals

**Goals:**

- Create a deterministic package directory layout that can be zipped or handed off.
- Generate a manifest containing version label, commit, generated time, included docs, included scripts, required services, default ports, and validation commands.
- Provide a verifier that checks package structure and emits JSON/Markdown readiness evidence.
- Add customer/operator docs for `.env`, first-admin initialization, backup, restore, upgrade, and handoff validation.
- Feed package verification into self-hosted delivery rehearsal and commercial baseline claims.

**Non-Goals:**

- No runtime license enforcement.
- No billing, SaaS tenancy, Marketplace/OAuth, enterprise SSO, or hosted secret vault.
- No full binary installer.
- No automatic backup of customer secrets.
- No claim that GitLab/Gitee/local-path importers are fully implemented beyond the existing bounded provider-aware setup states.

## Decisions

### Decision 1: Build a package directory, not an installer

The builder SHALL create a directory under `.tmp/self-hosted-package/<label>/` containing a manifest, docs, scripts, env template, and package README. It MAY later be zipped manually or by a CI step.

Alternative considered: build a platform-specific Windows/Linux installer. That adds maintenance burden and hides operational details too early. The current buyer path benefits more from transparent scripts and explicit evidence.

### Decision 2: Keep package verification deterministic and offline

The verifier SHALL inspect files and manifest structure without needing external network, provider credentials, or a running stack. Runtime smoke/readiness remains separate evidence in self-hosted delivery rehearsal.

Alternative considered: make package verification start Docker and run the full stack. That duplicates existing real-stack and rehearsal scripts and makes package checks fragile on machines without Docker permissions.

### Decision 3: Manifest is the package contract

The manifest SHALL be JSON so future release evidence and CI can parse it. Markdown output SHALL be generated for human handoff.

Alternative considered: docs-only package. That is easier to write but too weak for regression tests and readiness history.

### Decision 4: Package docs reference existing commands instead of duplicating behavior

The package README and runbooks SHALL reference canonical scripts (`start-real-stack`, `stop-real-stack`, `pre-release`, readiness collectors) instead of introducing parallel startup or validation logic.

Alternative considered: copy/paste all command details into package docs. That increases drift risk when scripts change.

## Risks / Trade-offs

- Package appears more complete than the product is → Mitigation: manifest and README preserve explicit unsupported/deferred lanes.
- Package verification passes while runtime deployment fails → Mitigation: verifier is labeled package-structure readiness; real-stack smoke remains separate required rehearsal evidence.
- Secrets are accidentally copied into handoff → Mitigation: builder only copies allowlisted docs/scripts/templates and excludes `.env`, `.tmp`, database files, logs, and provider credentials.
- Windows/Linux differences cause confusion → Mitigation: docs include both PowerShell and shell-oriented expectations where supported, with Windows one-click launcher as the current strongest path.
- Package output drifts from source docs → Mitigation: package builder copies canonical docs and records their paths in manifest.
