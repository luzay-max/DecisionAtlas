# ADR-0005: Durable Import Worker Lifecycle and Queue Ownership

## Status

**Proposed — direction endorsed, NOT accepted as implementation authority.**

On 2026-11-10 the maintainer endorsed PostgreSQL 17 as the primary durable queue backend and SQLite as an explicitly supported *local single-worker* mode. This is architecture-direction approval only. All recovery, factual, and release gates remain open; no runtime/schema/flag/deployment changes are authorized.

- Date: 2026-11-10
- Baseline: `main@3eb0eb94ee518164623b7f9dc85b91742985c055`
- Workstream: B07 — Worker reliability
- Authorization: ADR design and technical analysis only. No runtime code, schema, configuration, deployment, or feature-flag changes are authorized by this document.
- Related blocker: [Issue #36](https://github.com/luzay-max/DecisionAtlas/issues/36)
- Related integration boundary: [PR #47](https://github.com/luzay-max/DecisionAtlas/pull/47), which remains integration-only and must never be merged.

## 1. Context and verified current behavior

DecisionAtlas currently persists import-job records in the relational database, but execution is still attached to the FastAPI request process:

1. `POST /imports/github` calls `queue_github_import()`, which inserts a `queued` row in `import_jobs` and commits it.
2. The same API handler then registers `run_github_import()` with FastAPI `BackgroundTasks`.
3. `run_github_import()` conditionally changes `queued -> running`, then performs source import, indexing, and candidate extraction in one process-local task.
4. If that API process exits after the job row commits but before the background task is scheduled or completed, there is no independent worker that will discover and resume the job.
5. The operator-only `recover_import_jobs` command can inspect old jobs and, after all processes are stopped and an exact snapshot is supplied, mark one job failed. It intentionally does not replay work.

The existing implementation already has useful protections:

- Conditional status updates prevent a late or duplicate worker start from overwriting paused or terminal states.
- The source importer prefetches and validates selected Markdown before its Artifact write batch and commits the source batch atomically.
- Indexing replaces an Artifact's chunks and commits each Artifact's index update.
- **Extraction may commit candidates and SourceRefs mid-run:** `CandidateExtractionPipeline.run()` calls a progress reporter after inserting rows; `run_github_import()` passes the same SQLAlchemy session to `_build_extraction_progress_reporter()`, which calls `progress_session.commit()` when progress/time thresholds fire. The final pipeline commit is *not* the only commit. A crash can leave committed partial extraction rows.
- Safe pause checkpoints exist between selected stages; the worker must not wait for resume while holding a SQLite writer transaction.
- Offline recovery is explicit, snapshot-checked, and never automatically replays a partially completed job.

Those protections are not a durable worker protocol. The current `ImportJob` schema has no worker identity, lease, heartbeat, lease generation, attempt counter, retry schedule, or durable stage checkpoint. A job's age is not proof that its worker is dead.

### 1.1 Important repository evidence

The design is based on these current-main files and behaviors:

- `services/engine/app/api/imports.py`: import endpoints register `run_github_import` through FastAPI `BackgroundTasks`; pause/resume returns HTTP 503 unless `IMPORT_PAUSE_RESUME_ENABLED` is explicitly enabled.
- `services/engine/app/jobs/import_jobs.py`: process-local job execution, stage progression, safe checkpoints, and exception-to-failed handling.
- `services/engine/app/repositories/import_jobs.py`: conditional state transitions and manual offline recovery; no lease/fencing fields.
- `services/engine/app/jobs/recover_import_jobs.py`: inspection-only by default; applying recovery requires an exact job snapshot and an operator assertion that all workers are stopped.
- `services/engine/app/ingest/github_importer.py`: remote fetch/prefetch occurs before the source Artifact batch; the Artifact batch is committed as one transaction.
- `services/engine/app/indexing/index_artifact.py`: per-Artifact chunk replacement and commit.
- `services/engine/app/extractor/pipeline.py` and `services/engine/app/jobs/import_jobs.py`: candidates and SourceRefs may be committed *during* extraction by the shared-session progress reporter, as well as by the final pipeline commit.
- `services/engine/app/db/session.py`: SQLite connection setup uses a 30-second timeout and runs `PRAGMA busy_timeout=30000` during initialization, but does **not** explicitly enable WAL in that path. WAL cannot be assumed; connection-local PRAGMA application needs its own review.
- `services/engine/app/repositories/artifacts.py`: Artifact upsert is currently a select-then-insert/update operation; the inspected model does not declare a database uniqueness constraint for its logical identity.
- `services/engine/app/repositories/decisions.py` and `source_refs.py`: candidate and evidence rows are inserted; they do not currently expose a durable extraction-result idempotency key.
- `services/engine/app/config.py` and `services/engine/pyproject.toml`: no Engine `REDIS_URL` setting or Redis client dependency is declared in the inspected execution path.
- `docker-compose.yml` starts Redis, while the current Engine import endpoint still uses FastAPI `BackgroundTasks`. ADR-0001 originally named Redis for background coordination, but the current import execution path does not wire Redis into job claiming or delivery.

The above is a code-path review, not a claim that Redis is absent from every future or external deployment component.

## 2. Problem statement

The worker lifecycle must provide:

1. Durable discovery of queued work independently of API process lifetime.
2. Atomic single-owner claim under multiple worker processes.
3. A lease and heartbeat that distinguish a live worker from an abandoned claim.
4. Fencing so a stale worker cannot commit after a newer worker has reclaimed the job.
5. Explicit pause/resume semantics that cannot race with claim or terminal completion.
6. Safe crash/restart behavior at every stage boundary.
7. Bounded retries that do not duplicate committed Artifacts, chunks, candidates, or externally billed work without an explicit policy.
8. A supported and honest distinction between PostgreSQL multi-worker operation and SQLite demo operation.
9. Observable operational state and a manual reconciliation path when automatic recovery is unsafe.

“Exactly once” execution cannot be promised across a process crash and an external provider call. The design must instead combine at-least-once job delivery with idempotent local effects, fenced commits, and explicit handling of uncertain external outcomes.

## 3. Decision proposal

### 3.1 Use the relational database as the queue of record

**Proposed choice:** use PostgreSQL-backed `import_jobs` rows as the durable queue and source of truth for job state. Run one or more independent Engine worker processes that poll and claim eligible rows.

- The API transaction creates the job row and commits it. The API does not own execution and does not schedule the work in FastAPI `BackgroundTasks`.
- A worker process discovers eligible rows from the database and claims them atomically.
- Job state, lease ownership, retry timing, and stage checkpoints are stored in the same database as the job and its domain effects.
- The database row is authoritative. A worker notification is only a wake-up hint; a missed notification must not lose a job.
- Redis may later be used as a best-effort notification channel to reduce polling latency, but it is not the queue of record and is not required for correctness.

This is a proposal for a future B07 implementation, not a current runtime change. If accepted, it supersedes only ADR-0001's choice of Redis as the authoritative background-job coordination mechanism; Redis may remain available for non-authoritative notifications.

### 3.2 PostgreSQL is the multi-worker correctness target

For PostgreSQL, claim work in a short transaction using a row-locking pattern such as:

1. Select one eligible job ordered by priority/availability/creation time with `FOR UPDATE SKIP LOCKED`.
2. Atomically change it to `running`, increment its lease generation and attempt counter, assign a worker ID and fresh opaque lease token, and set heartbeat/expiry timestamps.
3. Commit before doing network, embedding, or model work.

An equivalent single-statement CTE plus `UPDATE ... RETURNING` is acceptable if concurrency tests prove the same contract. The implementation must not rely on an application-side “select then update” race.

PostgreSQL database time should be authoritative for lease comparisons. Worker wall clocks must not decide whether a lease is expired. `SKIP LOCKED` avoids competing row locks, but does not guarantee FIFO/fairness, a lease, table-level lock freedom or idempotency.

### 3.3 SQLite remains a supported local single-worker mode

SQLite has a single-writer model and does not provide PostgreSQL's `SKIP LOCKED` semantics. Conditional updates can protect simple state transitions, but they do not remove write contention between a long import transaction and an independent control-plane write.

Proposed support boundary:

- A SQLite *database file* supports exactly one executing worker and initially one in-flight job. A second worker must be **rejected at startup** by a real OS-enforced, per-database exclusive lifetime lock (or equivalently proven local exclusion), not just documentation or a stale marker file.
- API and worker processes may be separate on the **same host/local filesystem**; cross-host and network-filesystem sharing are unsupported.
- Use SQLite-compatible short conditional claims with the same domain state machine and idempotency rules as PostgreSQL; do not claim multi-worker availability.
- After restart, never-started `queued` jobs may be discovered and claimed. Partially executed jobs require proven checkpoints and idempotent effects, or must enter manual intervention; never blindly replay.
- SQLite pause/resume stays **default-disabled**, regardless of a single worker, until #36's bounded file-backed HTTP/worker tests pass.
- The current session initialization does not explicitly enable WAL. A future WAL mode must prove startup configuration, durability, checkpointing and contention semantics; `busy_timeout` cannot remove the single-writer limit.
- Multi-worker correctness targets PostgreSQL 17 first. No silent fallback to unverified SQLite semantics.

### 3.4 Redis is not authoritative

Redis is not selected as the first durable queue because the current code does not wire it into Engine job delivery, the Engine dependency/configuration does not declare a Redis client or `REDIS_URL`, and the checked-in Redis configuration has append-only persistence disabled. Making Redis authoritative would introduce a second state system and a database/broker dual-write problem.

If a future throughput requirement justifies Redis Streams, RQ, Celery, or another broker, it must be introduced with a transactional outbox (or an equally strong recoverable publication protocol), broker durability configuration, consumer redelivery semantics, and reconciliation. That is a separate ADR/change, not an implicit part of this proposal.

## 4. Proposed lifecycle and state machine

Execution state and operator intent must not be conflated. The proposed externally visible lifecycle is:

| Current state | Event | Next state | Required behavior |
| --- | --- | --- | --- |
| `queued` | Worker claim | `running` | Atomic claim; lease assigned |
| `queued` | Pause before claim | `paused` | Claim predicate no longer matches |
| `running` | Admin requests pause | `pause_requested` | Durable intent; worker still owns lease |
| `pause_requested` | Worker reaches safe checkpoint | `paused` | Commit completed unit + checkpoint; clear lease |
| `paused` | Admin resumes | `queued` | Resume from persisted checkpoint; a worker must claim again |
| `running` | Successful finalization | `succeeded` | Fenced terminal transition |
| `running` | Non-retryable/exhausted failure | `failed` | Fenced terminal transition and classified reason |
| `running` | Lease expires | `retry_wait` or manual intervention | Only if checkpoint and side-effect policy permit safe retry |
| `retry_wait` | Retry time reached | `queued` | Eligible for a new fenced claim |

The exact public status vocabulary may be adapted to the existing API contract, but the semantics above are mandatory.

### 4.1 Claim versus pause race

The database must serialize the race:

- If the pause update wins while the job is still `queued`, the claim predicate fails and no worker starts it.
- If the worker claim wins first, the pause request records `pause_requested`; it must not pretend that the job is already paused.
- At the next safe checkpoint, the worker atomically persists its completed work and checkpoint, changes to `paused`, and releases its lease.
- Resume changes a paused job back to `queued`; it does not set `running` directly and does not attempt to revive the old process.
- A duplicate resume or duplicate worker notification must not create a second owner.

The worker must never sleep waiting for resume while holding a transaction that blocks the control plane. No progress callback may commit partial source data merely to make pause responsive.

### 4.2 Pause is cooperative, not cancellation

Pause takes effect at a documented safe checkpoint. An in-flight GitHub request, embedding request, or model call may finish before the worker acknowledges pause. The API must expose “pause requested” separately from “paused” if the operation has not yet reached a checkpoint.

Cancellation is not included in this ADR's initial proposal. The inspected API does not provide a cancellation endpoint; do not advertise cancellation or overload pause to mean cancellation.

## 5. Lease, heartbeat, and fencing proposal

A future additive migration is expected to introduce fields equivalent to:

| Field | Purpose |
| --- | --- |
| `worker_id` | Identifies the process/instance currently owning the job |
| `lease_token` or monotonic `lease_generation` | Fences stale owners; token must change on every successful claim |
| `heartbeat_at` | Records the last successful liveness renewal |
| `lease_expires_at` | Database-time deadline after which a job may be considered abandoned |
| `attempt_count` | Counts successful claims/attempts, not arbitrary polling |
| `available_at` / `next_attempt_at` | Supports delayed bounded retry |
| `checkpoint_version` | Allows checkpoint format evolution |
| `checkpoint_json` | Stores durable stage/cursor and idempotency progress |
| `pause_requested_at` | Persists control-plane intent independently from worker acknowledgement |
| `last_failure_category` | Stable retry/operations classification |

Names and exact nullability are not final schema decisions. No migration is authorized in this design-only phase.

### 5.1 Heartbeat

- A claimed worker renews its lease at a cadence materially shorter than the lease TTL (provisional target: heartbeat around one-third of the TTL).
- Renewal is a conditional update on job ID, current lease token/generation and an **unexpired lease based on database time**, while the worker owns the job in either `running` **or** `pause_requested`. A pause request does not revoke the current lease: the worker keeps heartbeating until it commits the current bounded unit, records the checkpoint, transitions to `paused`, and releases the lease.
- Renewal must use a separate short-lived database session/connection from long-running stage work; it must not reuse a session that holds a source-write or extraction transaction.
- A renewal that updates zero rows means ownership has been lost. The worker must stop before committing further local effects. **An expired lease cannot be renewed even if no other worker has reclaimed it:** only a new atomic claim creates a fresh lease generation.
- The lease TTL, heartbeat interval, network timeout budget, and shutdown grace period must be measured and selected together; the provisional ratio is not a production setting.

### 5.2 Fencing is required, not optional

A lease timeout alone does not stop a paused, partitioned, or slow worker from waking up later. Every state transition and every durable stage write must be fenced.

Before a worker commits a unit of work, it must validate the current lease token/generation inside the same database transaction that commits the domain writes and checkpoint. The transaction must serialize against a reclaiming worker (for example by locking the job row on PostgreSQL). A pause request may allow the current bounded unit to finish, but it must prevent the worker from starting another unit. The current unit's effects, checkpoint, `pause_requested -> paused` transition, and lease release must be committed atomically. An expired `pause_requested` lease is handled by the same fenced recovery inspection as an expired `running` lease. A stale token must be unable to:

- update job progress or terminal state;
- publish staged Artifacts;
- replace ArtifactChunks;
- create Decisions or SourceRefs;
- advance a checkpoint.

Do not claim fencing if only the final `mark_succeeded` update checks the token while intermediate writes do not.

## 6. Checkpoints, transactions, and idempotency

The current pipeline has different commit boundaries. B07 must preserve evidence integrity while making those boundaries recoverable.

### 6.1 Source fetch and Artifact publication

Current behavior prefetches and validates source content, then writes the Artifact batch in one transaction. This protects against partial Artifact publication if a later fetch fails.

Do not casually replace this with arbitrary per-row commits: that would change the existing rollback contract.

Proposed direction for recoverable source ingestion:

1. Fetch remote pages/documents outside write transactions, with existing resource caps and source integrity checks.
2. Persist fetched payloads into job-scoped staging records in bounded transactions, keyed by stable source identity and content hash.
3. After the fetch/coverage phase is complete, publish/upsert the staged batch into visible Artifacts in a controlled transaction (or explicitly designed bounded publication units).
4. Advance the stage checkpoint in the same transaction as each publication unit.
5. On replay, reuse verified staging rows and idempotent Artifact identities; do not refetch/rewrite committed work without need.

This requires a design for staging retention, cleanup, and whether publication is atomic for the whole source batch or per bounded unit. That decision must be settled before implementation.

Artifact logical identity currently uses `(workspace_id, type, source_id)` in application code, but the inspected schema/repository path does not establish a database-enforced unique constraint and atomic upsert. Additive uniqueness and migration preflight are required before concurrent/replay claims can be considered safe.

### 6.2 Indexing

Indexing currently replaces chunks for one Artifact and commits that Artifact's update. This is a useful idempotent unit, but the job checkpoint is not currently committed atomically with the chunk replacement.

Proposed unit:

- compute embeddings outside a long write transaction;
- re-check lease/fencing;
- replace chunks and advance the per-Artifact checkpoint in one transaction;
- use a stable Artifact content hash and embedding/model version to skip already completed work;
- ensure duplicate execution cannot leave duplicate chunks.

Embedding calls can be billed and can time out ambiguously. Local chunk replacement can be idempotent; external embedding execution cannot be assumed exactly once unless the provider offers a usable idempotency contract.

### 6.3 Candidate extraction

This is the most important replay hazard in the current pipeline:

- screening and full extraction call an external provider;
- up to three full extraction calls can be in flight;
- candidate/SourceRef rows are inserted during extraction and **may be committed by the shared-session progress callback before the final pipeline commit**; crash recovery must account for partial committed results;
- the current “already extracted” check is based on whether an Artifact has a SourceRef;
- `DecisionRepository.create_candidate()` always inserts a new candidate, and SourceRef creation has no unique idempotency key.

A crash after a provider call but before the final commit can repeat provider work and incur another charge. A crash/replay after partial future evolution must not create duplicate candidates or refs.

Proposed direction:

- introduce a durable extraction-attempt/result record keyed by a deterministic operation identity such as `workspace_id + artifact_id + artifact_content_hash + extractor_version + prompt_version + provider/model`;
- record request fingerprint and attempt state before/after external calls;
- persist a normalized extraction outcome **including successful empty/no-decision results**, any candidate/SourceRefs, and the completed checkpoint atomically;
- add database uniqueness for the extraction operation identity and appropriate SourceRef identity;
- make reprocessing policy explicit when the source content, prompt, extractor, or model changes.

**Unknown provider outcome:** if a process dies after the provider accepted a request but before the result is durably recorded, the system cannot know whether the request was billed or completed. If the provider supports idempotency keys, pass the stable operation key. Otherwise mark the attempt as `outcome_unknown` and require an explicit bounded retry policy or operator reconciliation; do not promise exactly-once calls or silently replay unlimited paid work.

### 6.4 Retry classes

Retries must be stage- and failure-specific:

| Failure | Proposed policy |
| --- | --- |
| GitHub transient connect/read/TLS/5xx | Bounded retry with exponential backoff and jitter, respecting total request/time budget |
| GitHub `403`/`429` confirmed primary/secondary rate limit | Inspect `Retry-After`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` and documented rate-limit error signals; respect reset/Retry-After or at least 60 seconds for a secondary limit with no header; bounded backoff and total budget |
| GitHub `401`, confirmed permission/revocation `403`, inaccessible `404`, invalid input | Fail closed without blind retry; a private-resource `404` can conceal lack of access |
| Ambiguous `403` without clear rate-limit evidence | Classify as ambiguous, retain sanitized metadata, and stop or allow at most an explicitly bounded diagnostic retry; never loop indefinitely |
| Database serialization/deadlock/transient connection error | Retry only the current idempotent transaction after re-reading the fenced job state |
| Embedding timeout | Treat result as uncertain unless provider idempotency is available; bounded policy |
| LLM timeout/provider error | Record attempt and cost/unknown-outcome state; no unbounded automatic replay |
| Incomplete source coverage / integrity mismatch | Fail closed; do not publish an incomplete source batch as complete |
| Lease lost / stale token | Stop; do not write; a new owner controls subsequent work |

A job-level attempt limit must not multiply an already bounded per-request retry budget without an explicit total-call/cost ceiling.

## 7. Enqueue idempotency and workspace exclusivity

The current enqueue path checks for an active job before inserting, but that check alone is vulnerable to concurrent enqueue requests. The current webhook handler also checks for an active job in a **separate session/transaction** before calling `queue_github_import()`, and `trigger_delivery_id` has no verified database uniqueness constraint; both need a single transactional protocol.

Before multi-worker rollout:

- enforce at most one active import per workspace with a database constraint or an equivalent serializable enqueue protocol;
- include active/paused/retry-wait/pause-requested states in the exclusivity definition;
- define whether a new manual import may supersede or wait behind a webhook import;
- deduplicate webhook deliveries with a unique provider delivery identity and commit the delivery record and job creation in one transaction;
- define behavior when a webhook arrives while a manual import is active (coalesce, record pending, or reject with an auditable result).

No duplicate queue message or repeated webhook delivery may create two active import owners for the same workspace.

## 8. Worker process and operational behavior

Proposed future runtime topology:

- Fastify/FastAPI API: authenticate, authorize, validate, create durable job row, return job ID/status.
- Engine worker: independent process/service, polls PostgreSQL, claims with a lease, executes bounded stage units, renews heartbeat, checkpoints and releases/finishes.
- PostgreSQL: authoritative job, lease, checkpoint, idempotency, and domain state.
- Redis: optional notification only; database polling remains the recovery path.
- Web: displays queued/running/pause-requested/paused/retry-wait/succeeded/failed truthfully from Engine state.

Worker process requirements:

- stop claiming new jobs on SIGTERM;
- finish or safely checkpoint the current bounded unit within a configured grace period;
- release a lease only after durable checkpoint commit;
- if killed hard, let the lease expire and let a fenced recovery worker decide whether retry is safe;
- never mark a job failed solely because the API process restarted;
- never automatically replay a stage whose checkpoint or external side-effect outcome is ambiguous.

Operations must expose queue depth/age, oldest queued age, active workers, heartbeat age, lease expiry, attempt count, stage/checkpoint, retry delay, last failure category, and manual-intervention count. Logs must include job ID, worker ID, and lease generation, but never tokens, credentials, raw secrets, or sensitive provider payloads.

## 9. Alternatives considered

### A. Keep FastAPI BackgroundTasks

**Rejected for durable execution.** It is process-local, provides no independent queue consumer, and leaves a crash gap after the database row commits. It may remain suitable for short best-effort request-adjacent tasks, not the authoritative import worker.

### B. Make Redis Streams / RQ / Celery the authoritative queue

**Not selected for the first B07 design.** It adds a broker and another state machine beside the relational job/domain state. A database commit plus broker publish can lose or duplicate messages unless an outbox/reconciliation protocol is added. The current Engine does not declare a Redis client/configuration in the import execution path, and the checked-in Redis configuration is not an adequate basis for assuming durable queue semantics.

Revisit only if measured throughput or scheduling requirements justify a broker and a separate ADR defines the outbox, durability, redelivery, consumer groups, and reconciliation contract.

### C. PostgreSQL-backed queue with independent worker (proposed)

**Preferred.** It keeps job state, leases, checkpoints, and domain writes in one transactional system; PostgreSQL can atomically claim rows with row locking and `SKIP LOCKED`; and it avoids making Redis a second source of truth.

Costs include polling load, PostgreSQL-specific claim implementation, additive migrations, operational worker deployment, and the need to make every stage idempotent/fenced.

### D. SQLite multi-process queue with a sidecar control database

**Rejected for the initial design.** A separate control database cannot atomically coordinate with Artifact/candidate writes in the application database. It would introduce split-brain pause/lease state and difficult recovery semantics. SQLite remains a constrained single-worker/demo target, not the multi-worker correctness target.

## 10. Required acceptance matrix before implementation can be considered complete

All tests must use isolated databases and deterministic synchronization (barriers/events), not sleeps as the sole race proof.

### PostgreSQL 17 — mandatory

- [ ] Two or more workers racing to claim one job: exactly one claim succeeds.
- [ ] Two different jobs can be claimed concurrently without duplicate ownership.
- [ ] A paused-before-claim job is not claimed.
- [ ] Claim wins before pause: API records `pause_requested`; worker keeps its lease heartbeat, finishes at most the current bounded unit, starts no new unit, and acknowledges `paused` at a safe checkpoint.
- [ ] Pause acknowledgement commits stage effects and checkpoint atomically, then releases the lease.
- [ ] Resume returns the job to claimable state and exactly one worker continues from the checkpoint.
- [ ] Heartbeat renewal is conditional on the current lease token/generation, remains valid during `pause_requested`, and stops only after the pause checkpoint releases the lease.
- [ ] Expired lease can be reclaimed; a stale worker with the old token cannot commit job state or any domain effect.
- [ ] Worker SIGTERM at every stage boundary checkpoints/relinquishes safely; hard process kill is recovered according to stage policy.
- [ ] Crash after source fetch, after staging, during publication, after one Artifact index, during extraction, after provider response but before result persistence, and after result persistence each has a deterministic expected outcome.
- [ ] Artifact, chunk, candidate, and SourceRef writes are idempotent under duplicate delivery and lease reclaim.
- [ ] Concurrent enqueue and duplicate webhook delivery cannot create two active jobs for one workspace.
- [ ] Bounded retry/backoff, Retry-After, attempt ceiling, and unknown provider outcomes are verified.
- [ ] No credential, access token, raw secret, or provider request body appears in logs or job metadata.

### SQLite — explicit constrained-mode acceptance

- [ ] One worker only; duplicate claim and terminal-state CAS remain correct.
- [ ] No claim of multi-worker or cross-process high availability.
- [ ] Pause/resume remains disabled unless bounded control-plane latency and writer-lock behavior are positively proven for the exact SQLite deployment mode.
- [ ] The existing file-backed SQLite writer-lock reproducer is converted into a positive test only if the selected semantics genuinely resolve it; otherwise it remains an explicit expected limitation and the feature stays disabled.
- [ ] Offline snapshot-based manual recovery remains read-only by default and cannot be applied while any worker is alive.

### API/UI and operations

- [ ] API enqueue is durable even if the API process exits immediately after commit.
- [ ] UI distinguishes `pause_requested` from `paused` and never reports a control action as complete before worker acknowledgement.
- [ ] Unauthorized roles cannot pause/resume or inspect another workspace's job.
- [ ] Queue/lease metrics, logs, alerts, graceful shutdown, and operator reconciliation are documented and tested.
- [ ] Full exact-head CI plus PostgreSQL 17 workflow passes; no production rollout is inferred from unit/CI results alone.

## 11. Proposed B07 sequence (not yet authorized)

| Step | Deliverable | Gate |
| --- | --- | --- |
| B07-D0 | This ADR and independent technical review | Resolve architecture questions; maintainer accepts or rejects the ADR |
| B07-D1 | State-machine and schema design detail, including migration/backfill/rollback | Separate approval before any schema/runtime implementation |
| B07-I1 | PostgreSQL durable claim, worker process, lease and heartbeat | Separate implementation authorization; claim/fencing tests first |
| B07-I2 | Stage checkpointing and idempotent source/index/extraction effects | Separate implementation authorization; no unbounded provider replay |
| B07-I3 | Pause/resume acknowledgement and crash/restart recovery | Issue #36 acceptance matrix passes; only then consider enabling capability |
| B07-I4 | Operations, metrics, deployment and rollback rehearsal | Separate operational acceptance; no implicit production deployment approval |

The current authorization covers **B07-D0 only**: design and technical analysis. It does not authorize B07-D1 schema changes, any B07-I implementation, a code PR, production configuration, or deployment.

## 12. Open decisions for independent review

1. Should the first durable worker target be PostgreSQL 17 only, with SQLite explicitly single-worker and pause-disabled?
2. Should the initial queue use database polling only, or should Redis be added solely as a best-effort wake-up channel after the durable DB design is proven?
3. What is the supported import concurrency: one active job per workspace, plus a global worker limit? How are manual and webhook triggers coalesced?
4. What lease TTL, heartbeat interval, shutdown grace, and maximum uninterruptible provider operation are justified by measured latency?
5. Should source publication use job-scoped staging tables to preserve current all-or-nothing Artifact visibility while enabling resumable fetch?
6. What retention/privacy policy applies to normalized provider results and extraction-attempt records?
7. For providers without idempotency keys, should an unknown LLM/embedding outcome require operator review, or may one explicitly bounded retry be allowed with a documented duplicate-cost risk?
8. Should pause remain a cooperative checkpoint-only feature, and should cancellation be a separate future design?
9. What is the policy for an import that loses its access source or authorization while queued or running?
10. What schema migration and rollback guarantees are required for existing active/paused jobs?

No implementation should begin while decisions that affect fencing, replay safety, or data visibility remain unresolved.

## 13. Boundaries and non-goals

- **Issue #36 remains OPEN.** This ADR is not a fix, closure, or authorization to enable `IMPORT_PAUSE_RESUME_ENABLED`.
- **#34 remains unmigrated and unauthorized.** No schema migration/backfill or production application is included.
- **#47 remains Draft, integration-only, and must never be merged.**
- B07 code implementation is not authorized. No Worker service, queue client, schema, migration, runtime flag, or configuration is changed by this ADR.
- C01 is not started or authorized.
- No production deployment, private-source operation, credential rotation, paid model call, automatic worker replay, or worker enablement is authorized.

## References

- [Issue #36 — import control-plane and worker lifecycle blocker](https://github.com/luzay-max/DecisionAtlas/issues/36)
- [ADR-0001 — initial MVP stack](0001-mvp-stack.md)
- [Import pause/resume OpenSpec contract](../../../openspec/specs/import-pause-resume/spec.md)
- [GitHub import retry OpenSpec contract](../../../openspec/specs/github-import-retry/spec.md)
- [B06d-1 Imports contract](../../plans/2026-11-07-stage-b-b06d1-imports-contract.md)
