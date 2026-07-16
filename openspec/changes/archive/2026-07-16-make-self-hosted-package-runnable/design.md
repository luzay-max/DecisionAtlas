## Context

`build_self_hosted_package.py` describes its output as a `source_tree_handoff`, and the generated README tells an operator to run `scripts/dev/start-real-stack.ps1`. That launcher resolves the package root and requires `docker-compose.yml`, the pnpm workspace, `apps/api`, `apps/web`, `services/engine`, prompts, migrations, and demo helpers. The builder currently copies none of those runtime assets, while the verifier only checks docs, templates, scripts, and manifest metadata. This creates a false-positive package pass and prevents a clean external machine from exercising the advertised product.

The package must remain suitable for self-hosted handoff: no `.env`, repository/provider tokens, imported source, databases, logs, dependency directories, build output, or local caches. It is still a source package rather than a binary installer or container registry release.

## Goals / Non-Goals

**Goals:**

- Produce a deterministic source-tree package that can install dependencies and launch the existing engine/API/web stack without reading files from the maintainer checkout.
- Preserve exact Node and Python dependency inputs and the Docker Compose infrastructure required by the launcher.
- Make the manifest and verifier distinguish runnable runtime assets from operator documentation.
- Exercise a copied package in an isolated directory through dependency preflight, service startup, health checks, and browser smoke.
- Run the same package-level smoke on a fresh GitHub-hosted Windows runner and preserve its independent-but-not-customer-controlled evidence boundary.

**Non-Goals:**

- Building signed binaries, OCI release images, an online installer, auto-update, runtime licensing, billing, hosted multi-tenancy, or Marketplace distribution.
- Embedding provider keys, GitHub tokens, private repository contents, customer data, generated databases, or dependency caches.
- Claiming that a GitHub-hosted runner is a customer-controlled host.

## Decisions

### 1. Use explicit runtime allowlists, not a repository-wide copy

The builder will define required root files and required runtime trees. Runtime trees will be copied with a denylist for secrets, caches, build output, tests that are not used by package smoke, and generated data. Explicit allowlists make the package reviewable and prevent a future local directory from silently entering the handoff.

Alternative considered: copy the entire Git checkout and apply `.gitignore`. Rejected because `.gitignore` is not a secret-distribution policy and can include local or customer-specific files that are valid Git inputs but invalid package contents.

### 2. Keep source and evidence assets separate in the manifest

The manifest will add a runtime section containing copied root files, runtime trees, dependency commands, startup command, smoke command, and package type. Existing docs/scripts/templates sections remain for compatibility. The verifier will require both categories and report missing runtime assets as blocking.

Alternative considered: append runtime paths to the existing scripts list. Rejected because that would preserve the current false equivalence between “handoff documentation exists” and “application can run.”

### 3. Rehearse from the copied package root

The clean rehearsal will validate runnable entry points in its isolated package copy. A dedicated runtime mode will run dependency installation/preflight and service/browser smoke with the copied package as the working directory. Commands and output will be bounded in JSON/Markdown; secrets and raw repository/model content will not be recorded.

The local full rehearsal may use Docker PostgreSQL/Redis through `start-real-stack.ps1`. The GitHub-hosted runner will use the existing SQLite smoke stack because Windows hosted runners do not provide a reliable Linux Docker daemon. Both prove package independence; only external customer input can prove customer control.

### 4. Reuse the existing real-repository browser flow

The package will include the minimum Playwright configuration and imported-workspace core-loop spec needed for a runnable smoke. The repository input remains configurable so local evidence can use a freshly selected public repository. CI may use a stable public repository to avoid converting GitHub availability into product behavior.

### 5. Preserve compatibility and fail closed

The verifier will continue reading schema-v1 packages but classify a package without runtime metadata/assets as blocking for runnable handoff. Existing structure-only evidence remains historically readable and must not be relabeled as runnable proof.

## Risks / Trade-offs

- [Package size grows materially] -> Copy only runtime source and configuration; continue excluding dependencies, build output, caches, tests outside the bounded smoke, and generated data.
- [Allowlist misses a transitive runtime file] -> Add install/build/start preflight tests from the copied package and make missing imports or manifests blocking.
- [Source files contain accidental secrets] -> Keep path deny rules, scan package file names/content for bounded secret signatures, and never copy `.env` or runtime evidence directories.
- [GitHub runner smoke is mistaken for customer proof] -> Emit host class and `is_customer_controlled=false`; keep customer-host proof level non-clean.
- [Dependency downloads make the package not fully air-gapped] -> Describe this artifact as an offline-transfer source package with online dependency installation unless caches/images are supplied separately; do not claim fully air-gapped installation.
- [Longer CI] -> Put package runtime rehearsal in a path-filtered dedicated workflow and keep normal unit CI unchanged.

## Migration Plan

1. Extend builder and verifier while retaining existing manifest fields.
2. Add tests for runtime inclusion, exclusion, legacy blocking, and isolated rehearsal.
3. Build a fresh package and verify/install/start it from a directory outside the source tree.
4. Add and run the GitHub-hosted package rehearsal workflow.
5. Archive evidence and update self-hosted documentation, taskbook, and next plan.

Rollback is a normal Git revert. Previously generated packages remain readable as historical structure-only artifacts but are not valid runnable handoff packages.

## Open Questions

- A future change may replace source installation with prebuilt OCI images or a signed installer after real pilot feedback; this change does not choose that distribution model.
