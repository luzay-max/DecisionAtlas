# Pilot Commercial Proposal Kit

[Home](../../README.md) | [Pilot Delivery Kit](pilot-customer-delivery-kit.md) | [Quote Template](pilot-paid-quote-template.md) | [Acceptance Checklist](pilot-acceptance-checklist.md) | [Support And Renewal](pilot-support-renewal-upgrade-boundary.md) | [License Boundary](self-hosted-license-and-support-boundary.md)

---

Use this kit when a self-hosted evaluation is ready to become a bounded paid pilot discussion. It turns the technical delivery material into a customer-ready commercial proposal without adding billing, hosted multi-tenancy, Marketplace OAuth, hosted secret vault, online license server, or runtime license enforcement.

These files are proposal templates. They are not legal contracts, invoices, payment records, or signed customer agreements. Fill customer-specific versions outside this public repository or in a private customer-controlled delivery folder.

## Target Buyer

- Engineering lead or CTO who owns architecture decision quality.
- Small team operator who can run a customer-controlled self-hosted stack.
- Buyer who wants private repository analysis without sending source code, tokens, provider keys, or `.env` files to a hosted vendor.

## Paid Pilot Offer

The recommended paid pilot is a bounded self-hosted proof of value:

- Deploy DecisionAtlas in the customer's environment or an operator-controlled private environment.
- Import one representative public or private repository.
- Review a small set of candidate decisions.
- Run why-search and drift review against accepted decisions.
- Generate release evidence, hosted/operator readiness, benchmark comparison, readiness history, private-repo evidence when applicable, backup/restore/upgrade rehearsal evidence, and a Code Decision Audit report.

## Proposal Materials

| Material | Path | Purpose |
| --- | --- | --- |
| Quote assumptions | `docs/project/pilot-paid-quote-template.md` | Draft paid pilot price, term, deliverables, exclusions, and extension assumptions. |
| Acceptance checklist | `docs/project/pilot-acceptance-checklist.md` | Defines evidence-backed success criteria before the pilot is accepted. |
| Support and renewal boundary | `docs/project/pilot-support-renewal-upgrade-boundary.md` | Explains support response boundary, renewal path, upgrade path, and deferred capabilities. |
| Code Decision Audit template | `docs/project/code-decision-audit-template.md` | Customer-readable outcome report for paid pilot handoff. |
| Private repo evidence template | `docs/project/private-repo-pilot-evidence-template.md` | Sanitized proof path for private repository claims. |
| Backup restore upgrade rehearsal | `docs/project/backup-restore-upgrade-rehearsal.md` | Continuity evidence boundary for long-term self-hosted operation claims. |

## Evidence Required Before Sending

Attach or explicitly mark as `operator_guided`, `known_limitation`, `not_provided`, `warning`, or `blocking`:

- Package verification JSON/Markdown.
- Clean self-hosted install rehearsal JSON/Markdown.
- Release evidence JSON/Markdown.
- Hosted/operator readiness JSON/Markdown.
- Readiness evidence history entry.
- Real-repo benchmark comparison evidence.
- Public GitHub import rehearsal evidence when public-repo value is claimed.
- Private-repo pilot evidence verification when private-repo value is claimed.
- Backup/restore/upgrade rehearsal evidence before long-term continuity claims.
- Team handoff report when team workflow readiness is claimed.
- Code Decision Audit report for the selected repository.

## Draft Proposal Flow

1. Confirm the customer can run a self-hosted stack or has an operator who can run it.
2. Select one representative repository and one pilot owner.
3. Fill a private copy of the quote assumptions template.
4. Attach the acceptance checklist and evidence requirements.
5. Review the support boundary, renewal path, upgrade path, and deferred capability boundaries.
6. Keep filled customer-specific pricing, payment data, contact details, signed legal terms, source code, repository tokens, provider keys, and private issue or pull request text outside this repository.

## Verification

Generate proposal kit verification evidence:

```powershell
python scripts\ci\verify_pilot_commercial_proposal_kit.py `
  --output-json .tmp\pilot-commercial-proposal-kit-verification.json `
  --output-markdown .tmp\pilot-commercial-proposal-kit-verification.md
```

The verifier checks structure and boundary references only. It does not validate a negotiated customer contract or payment.
