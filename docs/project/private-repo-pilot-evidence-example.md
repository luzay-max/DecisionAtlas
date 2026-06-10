# Private Repo Pilot Evidence Example

Generated at: `2026-06-10T00:00:00+00:00`  
Status: `operator_guided`  
Evidence type: `private_repo_pilot_evidence`

This is a committed safe sample. It is not proof that a real private repository has been evaluated.

## Repository Scope

| Field | Value |
| --- | --- |
| Identity status | `redacted` |
| Provider | `github` |
| Access mode | `token` |
| Visibility | `private` |
| Repository label | `redacted-private-repository` |
| Environment | `customer_controlled_host` |

## Credential Custody

- Token material retained: `false`
- Token echoed to output: `false`
- Provider key retained: `false`
- Custody statement: Repository tokens and provider keys remain on the customer-controlled host and are not included in this evidence.

## Redaction Statement

This evidence contains only redacted labels, status values, counts, limitation categories, and operator notes approved for sharing.

Excluded from this example:

- raw private source content
- raw private issue or pull-request text
- raw model output
- token values
- provider keys
- customer identifiers
- local filesystem paths

## Workflow Lanes

| Lane | Status | Summary |
| --- | --- | --- |
| Token or installation setup | `operator_guided` | Operator configures least-privilege repository access locally. |
| Repository access validation | `operator_guided` | Operator validates access without exporting token material. |
| Private repository import | `operator_guided` | Run import in the customer-controlled environment and record count-only results. |
| Decision review | `operator_guided` | Record candidate and accepted decision counts only. |
| Why-search validation | `operator_guided` | Record grounded or insufficient-evidence outcomes without raw answers. |
| Drift review | `operator_guided` | Record drift state and false-positive notes without raw private artifacts. |
| Release and handoff evidence | `operator_guided` | Attach sanitized release/readiness/handoff/audit evidence when approved. |

## Count-Only Metrics

| Metric | Value |
| --- | --- |
| Imported artifact count | `not_provided` |
| Candidate decision count | `not_provided` |
| Accepted decision count | `not_provided` |
| Review action count | `not_provided` |
| Why-search case count | `not_provided` |
| Drift case count | `not_provided` |

## Limitations

- This committed sample is not private-repository proof.
- Actual private-repository evidence must be generated locally or in the customer-controlled environment.
- Raw private source content, issue text, pull-request text, token material, and provider keys are intentionally excluded.

## Recommended Next Actions

- Run the private-repository pilot in the customer-controlled environment.
- Fill count-only outcomes after operator review.
- Run `verify_private_repo_pilot_evidence.py` before sharing sanitized evidence.

## Operator Review

Approved for external sharing: `false`  
Review required before sharing: `true`

A human operator must confirm redaction and customer approval before this evidence is used in a customer handoff.
