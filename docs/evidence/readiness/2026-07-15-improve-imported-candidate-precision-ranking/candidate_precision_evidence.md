# Candidate Precision Real-Repository Evidence

- Generated at: 2026-07-15T02:34:16.880079+00:00
- Commit: 2f57d70
- Status: pass
- Evidence basis: before = legacy confidence ordering reconstructed from the live payload; after = precision-ranked API ordering.
- Provider mode: openai_compatible

| Workspace | Candidates | Strong | Partial | Weak | Secondary duplicates | Top changed | Moved up | Moved down |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| github-jazzband-pip-tools | 27 | 21 | 6 | 0 | 0 | True | 12 | 15 |
| github-pallets-markupsafe | 5 | 4 | 1 | 0 | 0 | False | 2 | 2 |

## Interpretation

The API now exposes a deterministic ordering and explanation for every candidate. No candidate is automatically accepted, rejected, or deleted by this evidence collector.
