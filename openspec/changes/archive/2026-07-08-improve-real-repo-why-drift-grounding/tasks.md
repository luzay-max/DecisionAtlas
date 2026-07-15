## 1. Grounding Metadata

- [x] 1.1 Add bounded why/drift grounding reason metadata to imported workspace core-loop reports.
- [x] 1.2 Keep warning/pass/blocking status semantics unchanged while adding `lane_reasons` and `grounding_summary`.

## 2. Evidence Propagation

- [x] 2.1 Preserve grounding details through multi-repo live diagnosis JSON output.
- [x] 2.2 Show compact grounding details in multi-repo diagnosis Markdown.
- [x] 2.3 Include product-controlled grounding details in warning-lane reduction classified lanes and Markdown.

## 3. Verification

- [x] 3.1 Add unit tests for why-search and drift grounding reason output.
- [x] 3.2 Add unit tests proving warning-lane reduction surfaces product-controlled grounding details.
- [x] 3.3 Run targeted CI collector tests and `openspec validate --all --strict`.

## 4. Real Rehearsal And Records

- [x] 4.1 Run real local-stack evidence rehearsal with `n8n` and `rich` if the stack is available.
- [x] 4.2 Archive updated readiness evidence and record the update log/taskbook status.
