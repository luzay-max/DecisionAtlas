## Why

The generated self-hosted package currently contains documentation, templates, and launch scripts but omits the application source, workspace manifests, lockfiles, Docker Compose definition, and engine runtime. An operator who receives only that package cannot run its advertised startup command, so package verification can report `pass` for a non-runnable delivery artifact and external-host validation cannot begin honestly.

## What Changes

- Build a bounded runnable source package containing the Node workspace, web/API runtime, Python engine, prompts, database migrations, Compose support, and exact dependency lockfiles required by the existing launcher.
- Keep local secrets, imported repositories, databases, logs, caches, build output, virtual environments, and dependency directories excluded from the handoff.
- Record runtime assets and runtime-install/start commands in the package manifest and README.
- Make package verification and clean-install rehearsal fail closed when runnable entry points or runtime source are missing.
- Add an isolated package runtime rehearsal that installs dependencies and exercises engine, API, web, and browser smoke from the package copy rather than the developer source tree.
- Run the rehearsal on a fresh GitHub-hosted Windows runner while preserving that this is independent-host evidence, not customer-controlled-host proof.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `offline-self-hosted-release-package`: Require the source-tree handoff package and manifest to contain the bounded runtime needed to install and start DecisionAtlas outside the maintainer repository.
- `clean-self-hosted-install-rehearsal`: Require clean rehearsal to validate runnable package entry points and support an isolated runtime smoke without upgrading independent-runner evidence into customer proof.

## Impact

- Package builder and verifier under `scripts/ci/`.
- Clean install/runtime rehearsal scripts and tests.
- Self-hosted package/operator documentation and manifest schema.
- GitHub Actions workflow and archived readiness evidence.
- Generated package size increases because bounded application source and lockfiles are included; dependencies, build output, secrets, and runtime data remain excluded.
