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
8. A supported and honest distinction between PostgreSQL multi-worker operation and **SQLite local single-worker operation**.
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

PostgreSQL database time should be authoritative for lease comparisons. **Acquire the job row lock first, then obtain a fresh database clock sample (e.g., `SELECT clock_timestamp()` after lock acquisition)**; neither transaction-start `now()`/`CURRENT_TIMESTAMP` nor a statement-start timestamp from a statement that waited on a lock is safe for expiry validation. The bounded-write-transaction rule in §19 defines when a validated commit may complete after expiry. `SKIP LOCKED` avoids competing row locks, but does not guarantee FIFO/fairness, a lease, table-level lock freedom or idempotency.

### 3.3 SQLite remains a supported local single-worker mode

SQLite has a single-writer model and does not provide PostgreSQL's `SKIP LOCKED` semantics. Conditional updates can protect simple state transitions, but they do not remove write contention between a long import transaction and an independent control-plane write.

Proposed support boundary:

- A SQLite *database file* supports exactly one executing worker and initially one in-flight job. A second worker must be **rejected at startup** by a real OS-enforced, per-database exclusive lifetime lock (or equivalently proven local exclusion), not just documentation or a stale marker file.
- API and worker processes may be separate on the **same host/local filesystem**; cross-host and network-filesystem sharing are unsupported.
- Use SQLite-compatible short conditional claims with the same domain state machine and idempotency rules as PostgreSQL; do not claim multi-worker availability.
- After restart, **provably never-started** `queued` jobs may be discovered and claimed only once §20's cutover and workspace/source quarantine gates pass. A legacy `queued` status alone is not proof of no execution or side effects. Partially executed jobs require proven checkpoints and idempotent effects, or must enter manual intervention; never blindly replay.
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
- Renewal is a conditional update on job ID, current lease token/generation and an **unexpired lease checked with a fresh post-lock database time**, while the worker owns the job in either `running` **or** `pause_requested`. A pause request does not revoke the current lease: the worker keeps heartbeating until it commits the current bounded unit, records the checkpoint, transitions to `paused`, and releases the lease.
- Renewal must use a separate short-lived database session/connection from long-running stage work; it must not reuse a session that holds a source-write or extraction transaction.
- A renewal that updates zero rows means ownership has been lost. The worker must stop before committing further local effects. **An expired lease cannot be renewed even if no other worker has reclaimed it:** only a new atomic claim creates a fresh lease generation.
- The lease TTL, heartbeat interval, network timeout budget, and shutdown grace period must be measured and selected together; the provisional ratio is not a production setting.

### 5.2 Fencing is required, not optional

A lease timeout alone does not stop a paused, partitioned, or slow worker from waking up later. Every state transition and every durable stage write must be fenced.

Before a worker performs **any** domain write in a bounded commit unit, it must lock the job row, obtain post-lock database time, and validate its lease token/generation inside the same transaction that commits the domain writes and checkpoint. The transaction must serialize against a reclaiming worker (for example by locking the job row on PostgreSQL). A pause request may allow the current bounded unit to finish, but it must prevent the worker from starting another unit. The current unit's effects, checkpoint, `pause_requested -> paused` transition, and lease release must be committed atomically. An expired `pause_requested` lease is handled by the same fenced recovery inspection as an expired `running` lease. A stale token must be unable to:

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

**Rejected for the initial design.** A separate control database cannot atomically coordinate with Artifact/candidate writes in the application database. It would introduce split-brain pause/lease state and difficult recovery semantics. SQLite remains a supported, constrained **local single-worker** target, not a multi-worker correctness target.

## 10. Required acceptance matrix before implementation can be considered complete

All tests must use isolated databases and deterministic synchronization (barriers/events), not sleeps as the sole race proof.

### PostgreSQL 17 — mandatory

- [ ] Two or more workers racing to claim one job: exactly one claim succeeds.
- [ ] Two different jobs can be claimed concurrently without duplicate ownership.
- [ ] A paused-before-claim job is not claimed.
- [ ] Claim wins before pause: API records `pause_requested`; worker keeps its lease heartbeat, finishes at most the current bounded unit, starts no new unit, and acknowledges `paused` at a safe checkpoint.
- [ ] Pause acknowledgement commits stage effects and checkpoint atomically, then releases the lease.
- [ ] Resume returns the job to claimable state and exactly one worker continues from the checkpoint.
- [ ] Heartbeat renewal is conditional on the current lease token/generation and a **fresh post-lock DB-time unexpired check**, remains valid during `pause_requested`, and stops only after the pause checkpoint releases the lease.
- [ ] Expired lease can be reclaimed; a stale worker with the old token cannot commit job state or any domain effect. Prove post-row-lock fresh clock sampling, lock wait crossing expiry, admitted unit committing just after expiry within timeout, concurrent heartbeat/reaper, unknown commit and old worker restoration.
- [ ] Worker SIGTERM at every stage boundary checkpoints/relinquishes safely; hard process kill is recovered according to stage policy.
- [ ] Crash after source fetch, after staging, during publication, after one Artifact index, during extraction, after provider response but before result persistence, and after result persistence each has a deterministic expected outcome.
- [ ] Artifact, chunk, candidate, and SourceRef writes are idempotent under duplicate delivery and lease reclaim.
- [ ] Concurrent enqueue and duplicate webhook delivery cannot create two active jobs for one workspace.
- [ ] GitHub 403 privilege/rate/ambiguous classification; bounded retry/backoff, Retry-After/reset, attempt ceiling, provider cost budget and unknown outcomes are verified.
- [ ] No credential, access token, raw secret, or provider request body appears in logs or job metadata.

### SQLite — explicit constrained-mode acceptance

- [ ] One *enforced* local worker only (second process fails startup); duplicate claim and terminal-state CAS remain correct.
- [ ] No claim of multi-worker or cross-host high availability; API and Worker may be separate processes only on the same host/local filesystem.
- [ ] Pause/resume remains disabled unless bounded control-plane latency and writer-lock behavior are positively proven for the exact SQLite deployment mode.
- [ ] Assert actual SQLite journal mode and busy timeout per relevant connection; the existing file-backed SQLite writer-lock reproducer becomes a positive test only if the selected semantics genuinely resolve it; otherwise retain the expected limitation and keep pause/resume disabled.
- [ ] On restart, never-started queued jobs are discovered; partly executed jobs require verifiable checkpoints/idempotency or manual intervention. Offline snapshot-based manual recovery remains read-only by default and cannot be applied while any worker is alive.

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

1. PostgreSQL 17 multi-worker + local single-worker SQLite are direction-approved; which **enforceable cross-platform OS ownership lock, startup validation and transactional claim adapter** will implement SQLite safely?
2. Can the initial PostgreSQL queue use database polling only, and should future optional wake-ups use PostgreSQL LISTEN/NOTIFY? Is Procrastinate compatible with the actual SQLAlchemy/psycopg transaction and project-specific fencing requirements without a second authoritative job state?
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

## 14. Review-mandated protocol specification (2026-11-10; still Proposed)

The following is a **design contract to be independently reviewed**, not implemented SQL, committed migrations, benchmark results, or permission to enable workers. It addresses the maintainer's architectural direction review. PostgreSQL 17 is the initial multi-worker correctness target; SQLite is a supported local single-worker mode with the same domain lifecycle.

### 14.1 Actual current-main commit boundaries — factual baseline

These are observed code paths, **not** the proposed B07 transaction model.

| Current stage | Current commit boundary and behavior | Crash/replay consequence |
| --- | --- | --- |
| Enqueue | `queue_github_import()` inserts `queued` and commits; API registers FastAPI `BackgroundTasks` afterwards | API process can die after enqueue and before execution; no independent consumer |
| Worker start | `mark_running()` conditionally updates `queued -> running`, then commits | Only process-local task carries on; no durable lease |
| Import prefetch | GitHub source pages/documents fetched before source Artifact write batch; progress callback at pre-write checkpoint | Network work may be repeated without persisted fetch/checkpoint |
| Artifact write batch | Importer upserts source Artifacts together; `on_progress` may flush status but does **not** commit partial Artifacts; importer commits the batch, then caller commits the next-stage summary | Source batch rollback is preserved if not committed; committed batch may be reprocessed without durable stage identity |
| Indexing | `index_artifact()` computes embeddings then deletes/replaces chunks for one Artifact and calls `session.commit()` | Already indexed Artifacts may coexist with later not-yet-indexed ones; external embedding can be reissued |
| Extraction progress | `CandidateExtractionPipeline.run()` creates candidate/SourceRef rows then calls progress callback. `_build_extraction_progress_reporter(session=same_session)` calls `progress_session.commit()` whenever processed count is zero/completed, advances by five, or at least three seconds elapsed | **Some candidate/SourceRef rows can already be committed before extraction finishes**. Mid-run crash is **not** a whole-run rollback; a resume must enumerate durable extraction operations, including empty outcomes |
| Extraction end | Pipeline invokes final progress callback and its own `self.session.commit()` | The final commit is in addition to the earlier progress commits, not the only persistence point |
| Final state | `mark_succeeded()` performs a conditional terminal update and the caller commits | A failed final state update does not undo earlier committed Artifacts/chunks/candidates |

Baseline evidence: `services/engine/app/jobs/import_jobs.py`, `services/engine/app/extractor/pipeline.py`, `services/engine/app/indexing/index_artifact.py`, `services/engine/app/repositories/import_jobs.py`, and `services/engine/app/ingest/github_importer.py` at `main@3eb0eb94`.

**Design implication:** Never equate a job-level `failed` status with a full database rollback. B07 must preflight duplicates and plan how legacy partially committed candidate/SourceRef rows are detected and reconciled **before** enabling automatic replay. The existing progress reporter must not simply be moved to a separate SQLite writer without proving the transaction and lock behavior.

### 14.2 Protocol A — atomic enqueue and webhook deduplication

PostgreSQL design:

1. Authenticate workspace/owner, resolve source access, and validate the requested import mode before enqueue.
2. In **one short database transaction**, establish workspace serialization and test/create active-job exclusivity. Enforce it with a database-backed rule such as a partial unique index on `workspace_id` for `queued`, `running`, `pause_requested`, `paused`, `retry_wait`, and `manual_intervention` *where that status blocks a new import*, or an equivalent transactional workspace claim with proved uniqueness. Terminal states release the active reservation.
3. Persist a webhook delivery identity keyed by its trusted installation/source and GitHub `X-GitHub-Delivery` ID with a database-enforced unique key. **Commit delivery disposition and the queued job in the same transaction**; on duplicate/redelivery return the same recorded outcome/job without creating a new one. The current FastAPI handler accepts a missing delivery header (`Header(None)`): the future protocol must **reject automatic enqueue with a missing/invalid delivery ID** (or separately approve and prove a signed-payload fingerprint policy), rather than bypassing deduplication. GitHub redelivery preserves the delivery ID; signature verification remains required.
4. Manual and webhook triggers share one enqueue policy. Define whether an arrival during an active job coalesces, records one pending refresh, or returns an auditable conflict. Do not make the webhook's initial active check and job insert separate transactions.
5. After commit, return the job ID. Any optional notification is post-commit and **non-authoritative**; the worker must discover committed jobs by polling even if notifications are dropped.

Proposed first-version policy: **one active import per workspace**, total worker concurrency separately configured, no strict FIFO guarantee. Prevent starvation across workspaces using a deterministic candidate order, measured wait-age, and fairness metrics. The schema/partial-index design is **not authorized**, and must undergo existing-row duplicate preflight, upgrade compatibility, and explicit rollback review.

### 14.3 Protocol B — atomic worker claim

PostgreSQL claim is a **short transaction**:

1. Select eligible `queued` or due `retry_wait` row(s) ordered by availability/age using `FOR UPDATE SKIP LOCKED`, with a bounded batch size and checked workspace concurrency.
2. Under that row lock, generate a unique owner ID and a fresh opaque lease token/monotonic generation; increment attempt count; record database-time `heartbeat_at` and `lease_expires_at`; set status to `running`; commit.
3. Only **after commit** may the worker fetch GitHub content, call embeddings/LLM, or perform stage computation. No task row lock is held across network/model work.
4. An empty claim is normal. Poll with bounded exponential idle backoff and jitter; cap database connections and protect normal API latency.

`SKIP LOCKED` does not provide fairness, leases, or business-effect idempotency, and table locks may still block. Use PostgreSQL as the authoritative clock, and avoid long transactions in clock-sensitive checks.

SQLite claim has the same logical CAS transition but only after the process acquires its per-file exclusive lifetime lock; it must reject a second worker at startup.

### 14.4 Protocol C — lease, heartbeat, expiry, recovery ownership

- Ownership is represented by `job_id + lease_generation/token + worker_id`; the token/generation changes on **every** successful claim or recovery reclaim.
- Heartbeat in a separate **short-lived** DB session may renew only when job status is `running` or `pause_requested`, token/generation matches, and `database_time < lease_expires_at`. It atomically advances heartbeat/expiry. No old or already expired lease may renew, even if no new worker has claimed the job.
- A heartbeat failure or zero-row CAS causes the worker to stop initiating work and refuse further writes. It does **not** erase already-sent provider requests.
- A reaper may consider an expired job for recovery only after it has acquired the DB row lock/CAS and **resampled the database clock after any lock wait**. It must **advance the generation and invalidate the old owner** before releasing the row; eligibility for automatic replay is decided separately by persisted checkpoint, stage and unknown-effects policy. A write transaction that locked/validated during an unexpired lease may finish after the deadline only within its enforced bounded transaction window; the reaper waits and rechecks its final committed state.
- For `pause_requested`, the same owner keeps renewing until it safely commits the current bounded stage unit/checkpoint, changes to `paused` and releases the lease. If it expires before acknowledgement, the reaper must preserve the pause intent and classify recovery rather than pretending the job was already paused.
- Heartbeat/lease TTL, backoff and shutdown grace are **TBD after measurements** of DB write latency, remote call timeouts and worst uninterruptible stage durations. “Heartbeat at one-third of lease TTL” is only a provisional ratio; no fixed seconds or throughput/RTO promise is approved.
- Database outage, lost connection, SIGTERM, hard kill, lease expiry, and delayed old-worker wake-up each need a deterministic transition plus a fenced/restart acceptance test.

Lease recovery is not a blanket permission to replay. The automatic recovery state must distinguish `retry_wait`, `manual_intervention`, and a recoverable `queued` state.

### 14.5 Protocol D — stale-worker fencing for **all** durable effects

Every future write unit (Artifact batch publication, ArtifactChunks, extraction-result/Decision/SourceRef publication, checkpoint, progress, terminal status) must:

1. Start a **fresh clean Session** and short transaction with no pending ORM work; do not attach staged Artifacts/Decisions/SourceRefs first.
2. Lock the owning ImportJob row or perform an equivalent atomic DB-time lease/owner CAS **in the same transaction**. SQLAlchemy 2.x autoflush may emit SQL *before* a mapped query; enforce lock-first sequencing (clean Session and/or explicit `no_autoflush`) and forbid called repositories from committing/rolling back on their own.
3. **After the row lock is actually granted**, sample fresh PostgreSQL `clock_timestamp()` (not a cached `now()` or statement-start value), then verify current generation/token, `sample_time < lease_expires_at`, eligible state and pause intent. If the token is stale/expired at this admission check, abort **without any domain write**. An admitted, bounded transaction may commit just after expiry under §19; it does not permit starting another unit on that expired lease.
4. Write the domain effects **and** durable checkpoint/result/lease transition in that very transaction; commit.
5. Return success to the worker only after commit; if commit outcome is unknown, reread durable operation identities rather than blindly repeating effects.

A prior standalone token query followed by unprotected writes is insufficient. Row-level claim/renew/recovery operations must serialize with the same fenced write unit. No row lock is held while calling a provider. **The write unit itself must have a bounded database transaction duration**; if preserving all-or-nothing source publication cannot meet that bound for large imports, review an immutable staged revision plus atomic visibility switch, without exposing partial coverage or committing partial source state. A pause that wins first is acknowledged before the next bounded unit, while a pause racing an already-started unit can be acknowledged only at its safe boundary.

External HTTP/LLM calls cannot be fenced retroactively; fencing controls **local persistence**, not provider-side billing.

### 14.6 Protocol E — durable stage checkpoint and idempotency

| Unit | Proposed deterministic operation identity | Commit/recovery rule |
| --- | --- | --- |
| Enqueue / webhook | `workspace + source/installation + delivery_id` for webhook; one active workspace claim | Unique transactional delivery and workspace reservation; return existing outcome on duplicate |
| Fetched source | `workspace + source type + source ID + content/blob revision fingerprint` | Prefetch bounded by current coverage budgets, stage by job with provenance/version and TTL; do not expose incomplete source batch |
| Artifact publication | Existing logical identity `(workspace_id, type, source_id)` plus revision hash; validate null/legacy duplicates | DB uniqueness/upsert and the last publication checkpoint in one fenced commit. Preserve full-batch atomic visibility unless a separately approved publication policy changes it |
| Chunk/index | `artifact_id + content_hash + chunker_version + embedding_model/version + config_fingerprint` | Compute outside write lock; fenced replace chunks and per-Artifact checkpoint atomically; ensure one row per logical chunk |
| Screening/extraction | `workspace + artifact ID + content_fingerprint + extractor/prompt/version + provider/model + effective config` | Durable outcome record for **positive, negative and successful empty/no-decision** results. Fenced, transactional result/candidate/SourceRef/checkpoint publication; unique operation ID prevents replay duplicates |
| Finished job | `job_id + lease_generation + final_checkpoint` | Fenced terminal state only after all required stage units/outcomes are durably reconciled |

The current check “any SourceRef exists for Artifact” cannot establish that a specific **content version** has completed extraction. A successful screening-out or no-decision result must also be persisted to avoid unbounded model calls after crash.

The current pipeline may already have **partially committed legacy candidate/SourceRef rows** via progress callbacks. Before first automatic replay, migration/preflight design must detect these and define safe reconciliation, review-state preservation, de-duplication, and no deletion of independently reviewed human decisions. **If historical results lack a provable operation identity, quarantine the affected workspace/source, including fresh enqueues, until explicit operator disposition; never synthesize historical provenance by hashing today's Artifact content.** Do not assume that a new future unique key retroactively identifies old rows. The operation fingerprint is **not** a substitute for Stage C's broader source-versioning design. The initial cutover must stop and fence off all legacy execution entry points: adding a generation check only in the new Worker cannot restrain old binaries (§20).

### 14.7 Protocol F — external request budget and uncertain results

- Persist a provider-operation record **before** dispatch: deterministic operation key, stage, model/provider, redacted request fingerprint, attempt number, deadline, budget reservation and status `pending`. Store no tokens, raw secrets or unnecessary private provider payloads.
- On a normal result, persist sanitized normalized output and operation outcome; publish candidate/chunks/checkpoint with the same fenced transaction whenever feasible.
- If the worker dies after dispatch but before a durable result, mark `outcome_unknown`. A provider with a documented idempotency key may safely use that key; otherwise **no automatic paid retry by default**. Require explicit operator/manual disposition or separately approved, strictly bounded duplicate-cost policy.
- Bound global job attempts, stage attempts, per-request retries, elapsed time, concurrent requests, and model/token/currency budget; avoid multiplication of nested retry budgets. Use a debit/reservation ledger and reconcile unknown outcomes rather than claiming exact billed cost.
- GitHub `403` and `429` can signal primary or secondary rate limiting. `Retry-After` and primary reset/remaining headers govern the next attempt; secondary limit without headers requires at least a one-minute wait and then bounded exponential backoff. Auth failure and unclassified `403` are not blindly retried. Exhausted budgets go to a classified terminal/manual state.
- For public-source ingestion, enforce existing coverage fail-closed policies and per-file/aggregate budgets; revalidate access/authorization on claim and at stage checkpoints as appropriate. Neither this design nor its review authorizes accessing private sources or making paid model calls.

### 14.8 Explicit recovery decision table

| Failure point | Proposed outcome after process/DB restart |
| --- | --- |
| Job insert committed but API process dies before dispatch | Independent worker polls and claims still-`queued` record; no task is lost because BackgroundTasks is no longer the only trigger |
| Worker exits before any work | Lease expires; new generation can claim **only if** durable stage evidence proves work and external effects did not begin and workspace quarantine is clear; status/age alone is insufficient |
| Remote fetch in progress, before durable stage | Re-fetch only within bounded coverage/idempotent source policy; no partially published Artifacts |
| Complete fetch staged but publication not committed | Verify staging integrity, resume publication from checkpoint; never publish incomplete coverage |
| Crash during fenced publication transaction | PostgreSQL transaction either committed or rolled back; reread operation identity/checkpoint before retry |
| Some Artifacts indexed | Skip already committed content/model-version units; continue missing Artifacts only |
| Extraction progress callback already committed some candidates | If original extraction identity is not independently provable, quarantine workspace/source; no automatic old-job replay **or new job bypass**, no retroactive fingerprint assignment, preserve reviewed decisions and SourceRefs |
| Provider request dispatched, outcome unknown | Mark `manual_intervention/outcome_unknown` unless provider supports real idempotent reconciliation |
| Pause requested and worker dies before checkpoint | Keep intent and reaper fencing; do **not** present `paused` as acknowledged until a valid checkpoint is recorded |
| Old worker wakes **without a previously admitted unit**, or after reaper advanced generation | No new job state/checkpoint/Artifact/chunk/candidate/SourceRef write may **start** or commit; a *previously admitted bounded unit* may commit just after expiry only under §19 while it still holds the job row lock, and the reaper must recheck after that commit |
| Database crash/failover | Recover only to **durably committed** state of chosen DB configuration; quantify RPO and do not promise zero loss without the required durability/replication settings |

No automatic replay of a stage with unknowable paid effects, missing operation identity, or unverified prior partial commits.

## 15. Queue-library comparison and initial execution choice

Choosing PostgreSQL does not require writing a generic queue framework from scratch. **First implementation direction: bounded project-specific domain queue, not Procrastinate.** The backend direction is approved, but neither this ADR nor any implementation is approved. Procrastinate remains a candidate only for a later documented reevaluation under §22.

| Candidate | Same-transaction enqueue | Fit for project-specific lease/fencing, pause, checkpoints | SQLite semantics | Main tradeoff |
| --- | --- | --- | --- | --- |
| Bounded custom PostgreSQL claim over `import_jobs` | Direct SQLAlchemy transaction | Full domain control; must implement/test every lease/reaper/locking invariant | Separate SQLite CAS/instance lock, shared domain state machine | More concurrency correctness code to own |
| Procrastinate (PostgreSQL job framework) | Official external-connection API allows job defer in caller-owned PostgreSQL transaction | Has mature queue/locks/retries; **must verify** domain fence on every Artifact/Decision commit, pause-ack semantics, operation results and mismatch between framework job and `ImportJob` status | Does not itself make the local SQLite mode a PostgreSQL queue; adapter still needed | Potentially less generic queue code, but risk of **two competing authoritative job states** |
| Redis/Celery as authoritative queue | Requires durable outbox/reconciliation to make DB + broker commit safe | Does not remove domain fencing/replay idempotency; delivery can repeat after worker crash | Would introduce extra runtime dependence | Premature second system/operational burden for this first version |

**Design-review acceptance questions:** Does Procrastinate's external-connection pattern work with the project's actual SQLAlchemy/psycopg version and transaction context (without hidden commits)? Can it expose/fence a domain ImportJob generation for each row write, and produce the required pause/resume acknowledgement? Can the project avoid duplicate authority between Procrastinate's job table and ImportJob? What additional DB connections, migration and maintenance requirements result? No unverified framework API compatibility may be assumed.

**Initial design choice:** use a **scope-limited, domain-specific queue** over authoritative `ImportJob`; separate PostgreSQL/SQLite claim adapters but one business state machine, and bounded database polling with backoff/jitter. **Do not adopt Procrastinate in the first version** and do not introduce it or Redis in this ADR PR. Procrastinate is not rejected forever; reevaluate only after fixed-version transaction integration, lifecycle/fencing, stale-retry policy, Windows behavior and net-maintenance benefit are demonstrated (§22).

A later `LISTEN/NOTIFY` optimization may only wake pollers; it is never the source of truth. Initial listener startup must first commit `LISTEN`, then recheck DB state to close the startup race; a missed notice or broken listening connection must always fall back to DB polling.

## 16. SQLite enforceable local-mode contract

SQLite is a real supported local/single-machine mode, **not** a promise of multi-process HA:

- Require the API and worker to access the same **absolute, canonical local database path**, not two relative URLs that silently create different files.
- **Chosen protocol (§21):** dedicated persistent sibling worker-ownership lock file, `flock(LOCK_EX|LOCK_NB)` on local Linux/POSIX targets and Windows `LockFileEx` exclusive nonblocking byte-range lock, held for the entire task-executor lifetime. This is an **execution eligibility** lock, not a SQLite write transaction. The second worker **fails startup**. Reject unverified path aliases and lock-file replacement; control descriptor/handle inheritance. All execution entry points must participate; legacy noncooperating executors are prohibited during cutover. Test Windows/Linux process behavior separately.
- Keep a durable owner/generation record for diagnostics and CAS, but stale owner timestamps or existence of a lock file alone do **not** establish that a process owns the DB.
- At most one executing import task for that database in v1. API and worker may be separate **same-host** processes; no network file system.
- Existing `busy_timeout=30000` is insufficient proof of pause responsiveness. Initialization does not explicitly set WAL; measure the actual pragma on each relevant connection, ensure positive lock-contention tests and configuration/checkpoint choices before claiming WAL behavior.
- Newly discovered **provably never-started** `queued` jobs may run after restart only after the cutover/quarantine gate passes. Merely being `queued` in legacy data is insufficient proof. Incomplete jobs with insufficient stage identity, earlier partially committed candidates, or ambiguous paid work require manual review instead of automatic resumption.
- Maintain the same domain states, permission checks, audit semantics and idempotent operation keys as PostgreSQL; **do not duplicate business flow logic**.
- Keep `IMPORT_PAUSE_RESUME_ENABLED=false` and do not close Issue #36 based solely on single-instance locking.

## 17. Durability assumptions, operations and performance gates

**Failure model / RPO:** Distinguish API-process loss, Worker crash, DB process crash, storage failure and replicated DB failover. PostgreSQL 17 is currently supported through 2029-11-08; maintain patch updates and test future versions rather than treating 17 as a permanent architecture pin. PostgreSQL 17 with synchronous durable commit on healthy storage can protect acknowledged local transactions against a DB process crash, but async commit may lose recently acknowledged transactions and async replication/failover may lose not-yet-replicated commits. Backups, `fsync`, `synchronous_commit`, replication topology, HA target, point-in-time recovery and measured restore RPO/RTO must be documented before production promises. No performance or failover experiment was run in this ADR phase.

**Operational metrics:** Queue depth, oldest queued age, enqueue-to-claim latency, per-workspace fairness/starvation, active workers and lease expiry, heartbeat failure, retries and lost leases, manual-intervention queue, duplicate delivery, provider budget/unknown outcomes, throughput, normal API latency and DB connections. Also monitor `import_jobs` dead tuples/table/index size, VACUUM/autovacuum activity, WAL generation/retention, transaction duration and cleanup/archival of old jobs and staging/results. Limit heartbeat rewrite frequency and avoid high-frequency writes to large JSON summaries.

**Capacity policy:** Start with finite worker concurrency and bounded backoff with jitter; no arbitrary throughput number or polling interval is approved without workload measurements. PostgreSQL 17 is the **current acceptance baseline, not a permanent version pin**. Track minor updates and test supported future major versions before upgrade.

**Release gate:** Observability and resource-pressure tests must establish API response latency under worker load, long-running transaction absence, queue fairness and saturation behavior; unit/CI green alone is not deployment readiness.

## 18. Additional acceptance gates from independent direction review

- [ ] Document/test **every actual current-main commit boundary**, especially same-session extraction progress commits and legacy partially committed candidates; no new enqueue or claim may bypass a workspace/source with unresolved legacy quarantine.
- [ ] Prove concurrent enqueue, duplicate webhook delivery and active workspace uniqueness using real PostgreSQL transactions and unique constraints (or equivalent locking).
- [ ] Verify short atomic claim, fair-enough polling, explicit ownership generation, lease expiry and post-expiry renewal rejection.
- [ ] Verify stale owners cannot commit **any** domain effect or checkpoint and that pause-requested owners heartbeat until safe acknowledgement.
- [ ] Persist extraction outcomes including **zero-result** and already committed legacy candidate data; safe restart does not duplicate Decisions/SourceRefs or reset human review state.
- [ ] Classify confirmed GitHub 403 permissions versus primary/secondary rate limit and unknown 403, applying bounded Retry-After/reset logic without blind retries.
- [ ] Default unknown paid-model outcomes to manual reconciliation, and demonstrate budget ceilings and no implicit duplicate billing claim.
- [ ] Reject a second SQLite worker process at startup using `flock` / `LockFileEx` over a **stable, nonreplaced** sidecar; prove alias rejection, child-handle inheritance protection, old-entry bypass prevention, cross-platform release on crash, same-host file semantics and actual journal mode. Test **provably never-started** queued restart versus quarantined incomplete work.
- [ ] Record initial **non-adoption of Procrastinate**, then run fixed-version reevaluation only if justified: SQLAlchemy 2.x/psycopg 3 transaction bridge, domain authority and fencing, pause/stalled recovery controls, Windows/Unix shutdown, migration overhead and total lifecycle maintenance cost.
- [ ] Define RPO/RTO per failure mode and acceptance for database storage/replica failure; test post-crash recovery without assuming every acknowledged async/replicated commit survives.
- [ ] Monitor queue bloat, WAL, autovacuum, CPU/connections, and API latency under load; do not assert a measured capacity before tests.

**Review disposition:** PostgreSQL 17 main queue plus supported SQLite local single-worker is **direction approved only**. ADR-0005 remains **Proposed** pending a separate, genuinely independent design review of these protocols and the unresolved schema/replay choices. No code, schema, migration, #34 action, #36 flag enablement, #47 merge, C01, paid model call or production deployment is authorized.

## 19. Lease admission, fresh-clock sampling and commit linearization (second design review)

**Decision: a short write unit admitted while a lease is live may finish after its expiry, but no new unit can begin after expiry.** A reaper must acquire the **same ImportJob row lock**, wait for an admitted unit to complete, and then recheck the *committed* state with a *fresh* clock. This gives a serialization boundary without pretending the lease timer can roll back a transaction already in progress.

### 19.1 Exact PostgreSQL protocol

1. Before any domain mutations, create a **fresh, clean SQLAlchemy Session** and begin a short transaction. Its identity map must contain no dirty/pending Artifact, Chunk, Decision, SourceRef or job changes. The transaction uses explicit bounded `lock_timeout` / `statement_timeout` (and monitored transaction elapsed time); numeric values must be based on tests, not guesses.
2. Lock the ImportJob row with an appropriate `SELECT ... FOR UPDATE`, or atomically serialize with an equivalent row-level conditional operation. **Only after the row lock is granted**, evaluate `SELECT clock_timestamp()` in a *subsequent* statement. PostgreSQL `now()`/`CURRENT_TIMESTAMP` use transaction start; `statement_timestamp()` uses statement start, which may predate a lock wait. Neither is sufficient after that wait. A `clock_timestamp()` embedded in the same waiting statement is not a substitute for explicitly sampling **after** lock acquisition.
3. Reject immediately if owner ID/generation mismatch, job state disallows the unit, or fresh `clock_timestamp() >= lease_expires_at`. A lease that expired while **waiting for the lock** cannot newly authorize writes even if the original statement started before expiry.
4. If admission succeeds while unexpired, write **only that bounded unit** (including its domain rows and checkpoint/result) and commit or roll back atomically. No provider/network request occurs inside this transaction; internal repositories must not `commit()`/`rollback()`/open an unrelated session. `no_autoflush` can additionally guard the admission query, but is **not** a substitute for a clean Session: ORM flush before lock breaks the required order and must fail code review/tests.
5. Once admitted, the short transaction **may commit after `lease_expires_at`** (example: validates at 10:00:29 with expiry at 10:00:30, commits at 10:00:31) **only within an enforced upper bound**. The lease is not renewed by this admission; the worker may not start a second write unit without a new valid lease. If that unit overruns the configured bounded transaction/lock budget, cancel and roll back rather than extending ownership indefinitely.
6. Renewal and reclaim use the same row-level serialization. A heartbeat unable to acquire the row lock may miss a renewal; the admitted write unit must be bounded and sized with a lease/heartbeat safety margin. A timed-out/failed heartbeat is **not** evidence that a new worker may write; recovery must lock the row and reclassify.
7. A reaper blocks (under its own finite lock timeout) until the admitted unit releases its row lock. After obtaining it, the reaper **rereads status, generation, checkpoint and a fresh `clock_timestamp()`**. If the unit already marked the job completed/paused, do not reclaim. Otherwise invalidate the old generation, then enter stage-specific recovery/quarantine. If reclaim won the lock first, the old worker's eventual admission check fails; no old domain write is allowed.
8. **Unknown COMMIT outcome** (connection lost near commit): do not treat it as an automatic rollback. A newly started transaction rereads the persisted operation identity, results and checkpoint; if ambiguous, mark for operator review, not blind replay.

**Linearization points:** claim/reclaim/heartbeat take effect on their committed row updates; an admitted domain unit becomes visible on its own transaction commit. A post-expiry admitted commit is allowed as above because reclaim cannot pass that row lock and must reread the result. The distinction between **lease expiry** and **commit admission** must be reflected in all tests and operator descriptions; do not claim “no commit after the timestamp.”

### 19.2 Required deterministic tests

- Worker waits on locked job row; lease expires while waiting; newly acquired lock + fresh time rejects the write (including versions using stale transaction/statement timestamps as negative controls).
- Worker admits at 10:00:29, lease expires 10:00:30, bounded unit commits 10:00:31; reaper waits, then sees the new checkpoint and only then classifies next action.
- Reaper obtains lock first after expiry; late worker fails admission and writes nothing.
- Heartbeat versus reaper, heartbeat blocked behind legitimate bounded write, and post-expiry renewal rejection.
- Dirty SQLAlchemy Session would autoflush before the lock; lock-first clean Session protects against this; repository-level hidden commits fail explicit transaction-contract tests.
- Old worker resumes after new generation; unknown commit result is resolved by operation-key readback, not a duplicate insert.
- Explicit lock/statement/transaction timeouts terminate an oversized write unit; confirm normal API and heartbeat latency remains bounded.

## 20. Legacy-partial-result quarantine and exclusive migration cutover

**Decision: unverifiable legacy extraction data is quarantined, not silently retrofitted with modern operation identities.** Historic rows may lack the exact source version, model, prompt, parameters and operation intent in effect when they were created. Hashing the *current* Artifact and assigning that fingerprint to historical Decisions/SourceRefs would invent provenance.

### 20.1 Recovery/re-enqueue decision table

| Persisted condition | Automatic claim/replay | Required disposition |
| --- | --- | --- |
| `queued` and **provably never executed**, no legacy effects/unknown sends, old executors stopped | Yes, after new protocol's clean-queue verification and unique workspace ownership | Claim under the new generation |
| B07-native checkpoint + complete immutable operation identity and all effects prove idempotent | Yes, only permitted stage(s) | Compare checkpoint/result keys, new generation and budget before resuming |
| Legacy `running`/`paused`/`failed`/incomplete job with unassignable committed candidates/refs or unknown stage progress | **No** | Quarantine job and affected workspace/source; exact evidence inventory + operator snapshot/approval needed |
| Prior human-reviewed Decision/SourceRef | **Never automatically delete, merge, overwrite or regress review state** | Preserve audit and references; operator determines any supersession or new import policy |
| Provider request/billing outcome unknown, without documented idempotency key/reconciliation | **No paid retry by default** | Durable unknown-outcome record and manual disposition |
| New job for an affected workspace with unresolved legacy quarantine | **No, even with a new job ID** | Enqueue and claim must enforce a durable workspace/source quarantine gate; explicitly recorded operator clearance first |

Quarantine is a **database-enforced or equivalently transactional state**, not an in-memory warning or UI-only filter. The enqueue transaction and every claim must read it under serialization with workspace active-job ownership. A rejected or parked new task must not bypass quarantine by changing repo spelling, job ID, webhook delivery, provider path, or retry mode. Domain/workspace/source identity normalization and owner scope must be considered. Where the prior operation cannot be tied to a specific source, quarantine conservatively at workspace level.

### 20.2 First deployment cutover protocol (future implementation only)

1. Enter a controlled maintenance window, **block new enqueue** (including Webhooks, CLI, schedules and API import routes), and stop all old import-capable instances, not just the new Worker. Inventory running FastAPI `BackgroundTasks`, CLI/recovery scripts, manual import commands, webhooks and any unattended entry points.
2. Ensure no old write transactions or provider calls remain active, with a finite drain/shutdown procedure and operator evidence. Merely waiting for a legacy status timeout is insufficient: old binaries do **not** understand generations and cannot be fenced by a new worker's checks.
3. Prevent the old executor from **restarting**: deployment manifests/process managers and entrypoint runtime/version gates must reject mixed execution epochs. Any allowed new write entry point must implement generation checks and the SQLite ownership gate. If reliable exclusion cannot be demonstrated, **do not enable automatic recovery or new workers**.
4. Back up the DB and record schema/binary versions plus exact active-job and domain-row snapshots. Inventory old jobs and partial candidate/SourceRef rows. Distinguish truly never-started queued jobs from jobs with missing/ambiguous execution history; when uncertain, quarantine.
5. Under the later separately approved migration, create future identity/quarantine records without inventing legacy fingerprints or altering reviewed decisions. Block **new** tasks for quarantined workspaces/sources until operator disposition is durably recorded. Require bounded read-only inspection default; any repair/deletion/upsert must have a separately authorized audit trail and rollback/backup.
6. Only after version exclusivity, schema compatibility, operator inventory and rollback rehearsal pass may the independent Worker be switched on. Old versions may **not** be restarted against the upgraded DB as a rollback shortcut. A rollback must first stop new writers and pass an explicit reverse-compatibility/restore plan.

No current GitHub commit, schema, migration or runtime cutover was performed by this ADR. **The approved design direction is not a cutover authorization.**

### 20.3 Acceptance

Reproduce: partially committed legacy candidates; absent prompt/model/source revision; empty-result legacy extraction; manually accepted/superseded decision; new manual import while a workspace is quarantined; webhook replay with a different delivery; legacy API/CLI execution trying to bypass the gate; mixed-version worker after deployment rollback. Every automatic bypass is a failing test.

## 21. SQLite concrete execution-ownership lock contract

**Chosen protocol, subject to OS integration validation:** a persistent sibling `<canonical-db-path>.worker.lock` file is a **worker-execution eligibility lock**, never a long-held SQLite transaction/database-write lock.

- **Identity and supported paths:** resolve database URL to one absolute canonical local filesystem file before any import worker/API execution path is enabled. Resolve symlink/junction components, but **reject** database or lock sidecar paths reached through symlinks/reparse points, hardlinks/multiple-link file identity, network drives and unverified container mount aliases until an identity-unification proof exists. On POSIX check `realpath`, device/inode and link count; on Windows check the volume/file identity, link count and reparse status with supported Win32 APIs. An uninspectable/ambiguous path is **startup error**, not a silent second lock.
- **Stable lock file:** create-once/open-existing `<canonical-db-path>.worker.lock` in the same local directory, with restrictive permissions. Lock it without truncating/replacing it. Verify the opened file's stable file ID/inode equals the path's currently resolved identity after acquisition and periodically before work; on mismatch **stop**. The lock file must **not be deleted, renamed, recreated, unlinked or manually “cleaned up”** during normal running, shutdown, crash repair, DB swap or migration; its existence alone does not indicate ownership.
- **Linux (and only tested POSIX variants):** acquire `flock(fd, LOCK_EX | LOCK_NB)` over the opened sidecar. Hold the same open file description for the **whole execution-owning process lifetime**, fail immediately if busy, and release by explicit unlock/close on orderly shutdown. Use `FD_CLOEXEC` and close/invalidate inherited lock descriptors in forked children; `fork` duplicates an open-file description and can unintentionally keep the lock held after the parent exits. Prohibit subprocesses from inheriting the execution entitlement.
- **Windows:** acquire an exclusive, fail-immediately `LockFileEx` byte-range lock on the same stable sidecar, retaining its non-inheritable file handle for the entire executing lifetime; release with `UnlockFileEx`/close. Use non-inheritable handles (`HANDLE_FLAG_INHERIT` cleared) and verify children cannot accidentally retain or impersonate ownership. Never rely on POSIX `flock` behavior on Windows. Test Windows service stop, force-terminate and new-process acquisition separately.
- **Mandatory application cooperation:** OS locks are advisory for noncooperating programs (especially Linux `flock`). **Every** task-executing entrance—new worker, legacy `BackgroundTasks`, direct `run_github_import` or CLI/manual script, webhook-triggered execution, scheduled runner and tests that actually execute imports—must call the shared ownership gate **before** any task work. A duplicate execution inside the same process also requires an in-process single-task guard. A DB session from an API handler may still serve ordinary reads, but may not execute imports without the gate. Legacy binaries unaware of the lock are excluded using §20 cutover, not presumed safe.
- **Recovery and file lifecycle:** worker crash causes OS release once all owning descriptors/handles close; test actual process death, not marker-file deletion. Any DB replacement, backup restore, migration, file move or lock-sidecar change requires stopping *all* related API/workers/CLI, verifying no open holders, then a coordinated maintenance/restore protocol; the persistent lock file is never replaced while any executable could still use the old identity.
- **Failure-closed defaults:** if platform lock semantics, local path identity, containment, child inheritance or all-entry participation is not proven, refuse Worker startup. This is a *design* for supported Windows/Linux; no live cross-platform behavior has been tested in this ADR phase. SQLite pause/resume remains disabled pending #36 acceptance. `busy_timeout` and WAL do not create ownership or multi-writer execution safety.

### 21.1 Required OS tests

Two workers racing startup; same-process duplicate task; SIGKILL/TerminateProcess then fresh worker; `fork` child, `exec` child and Windows subprocess with inherited-handle attempts; symlink/junction and hardlink aliases, relative vs absolute and case aliases, unsupported network/container mount; swapping/unlinking the lock file while held; replacing/restoring the database; old `BackgroundTasks`/CLI/webhook bypass; same-host separate API/worker; observed PRAGMA journal mode and 30-second busy timeout. Fail closed rather than making an untested locking guarantee.

## 22. Procrastinate disposition and reevaluation gate

**First-version decision: do not adopt Procrastinate.** Preserve it as a candidate, not as an automatic downgrade or impossible option. A scope-limited domain job queue over `ImportJob` is preferred because DecisionAtlas must in any case implement Fencing for every domain write, legacy quarantine, unknown-paid-outcome policy, pause acknowledgement, and SQLite's separate claim adapter.

**Concrete integration concerns:**

1. The Procrastinate external-connection API can defer tasks within a caller-owned PostgreSQL transaction, but its documented SQLAlchemy connector is **`SQLAlchemyPsycopg2Connector`**. Other connectors accept psycopg 3 native connections; neither fact proves a direct compatibility path with the project's SQLAlchemy 2.x + psycopg 3 `Session` and its commit/rollback/pool ownership. No compatible fixed-version integration has been executed.
2. Procrastinate tracks Worker heartbeat and finds stalled jobs, but its documented stalled-task recovery example performs **application-chosen retry**. It cannot infer legacy partial commits, settled human review, missing source fingerprints or ambiguous paid-provider requests. Its scheduler state must never overwrite the **authoritative `ImportJob` business state**, and domain Fencing is still required.
3. Official Windows documentation warns that Unix-style graceful signal shutdown is not equivalent on Windows; Windows CI/desktop support would need separate process-abort and recovery tests. The framework cannot replace SQLite mode just because the PostgreSQL variant works.
4. Maintaining two authoritative job truths or two incompatible lifecycle state machines would be unacceptable. If Procrastinate is evaluated later, `ImportJob` remains the only authority for domain eligibility/checkpoint/outcome; framework records can control delivery only.

**Reevaluation only when all are satisfied:** pin and document a tested Procrastinate release; show same-transaction SQLAlchemy 2.x/psycopg 3 enqueue/rollback without hidden commits or double-authority; demonstrate lease/recovery/fencing across every domain write; prove configurable “no replay on unknown paid/legacy” policy; pass Windows/Linux shutdown/recovery and SQLite adapter compatibility matrix; measure actual code/operations complexity improvement over bounded custom queue; obtain independent review and separate maintainer approval. Until then: **no Procrastinate dependency, worker code or additional queue infrastructure.**

## References

- [PostgreSQL 17 date/time functions: transaction, statement, actual clock](https://www.postgresql.org/docs/17/functions-datetime.html)
- [SQLAlchemy 2.0 Session autoflush and transaction boundaries](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Linux flock open-file-description inheritance and advisory semantics](https://man7.org/linux/man-pages/man2/flock.2.html)
- [Windows LockFileEx](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex)
- [Windows non-inheritable handles](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-sethandleinformation)
- [Procrastinate external DB connection and SQLAlchemy connector types](https://procrastinate.readthedocs.io/en/stable/howto/production/external_connection.html)
- [Procrastinate stalled-job retry policy](https://procrastinate.readthedocs.io/en/stable/howto/production/retry_stalled_jobs.html)
- [Procrastinate Windows process limitations](https://procrastinate.readthedocs.io/en/stable/howto/basics/windows.html)

- [GitHub webhook delivery ID and redelivery](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)
- [GitHub REST API primary/secondary rate-limit guidance](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- [SQLite WAL and local-filesystem constraints](https://www.sqlite.org/wal.html)
- [SQLite concurrency / when to use it](https://sqlite.org/whentouse.html)
- [PostgreSQL 17 SELECT / SKIP LOCKED](https://www.postgresql.org/docs/17/sql-select.html)
- [PostgreSQL LISTEN startup race](https://www.postgresql.org/docs/17/sql-listen.html)
- [PostgreSQL NOTIFY](https://www.postgresql.org/docs/17/sql-notify.html)
- [PostgreSQL 17 async-commit durability](https://www.postgresql.org/docs/17/wal-async-commit.html)
- [PostgreSQL 17 routine vacuuming](https://www.postgresql.org/docs/17/routine-vacuuming.html)
- [PostgreSQL support/versioning policy](https://www.postgresql.org/support/versioning/)
- [Procrastinate: external DB connection](https://procrastinate.readthedocs.io/en/stable/howto/production/external_connection.html)
- [Celery task idempotency and redelivery](https://docs.celeryq.dev/en/latest/userguide/tasks.html)
- [Issue #36 — import control-plane and worker lifecycle blocker](https://github.com/luzay-max/DecisionAtlas/issues/36)
- [ADR-0001 — initial MVP stack](0001-mvp-stack.md)
- [Import pause/resume OpenSpec contract](../../../openspec/specs/import-pause-resume/spec.md)
- [GitHub import retry OpenSpec contract](../../../openspec/specs/github-import-retry/spec.md)
- [B06d-1 Imports contract](../../plans/2026-11-07-stage-b-b06d1-imports-contract.md)
