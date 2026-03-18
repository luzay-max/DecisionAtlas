# DecisionAtlas v0.2 Release Notes

## What v0.2 adds

- runtime selection between fake provider mode and OpenAI-compatible live provider mode
- configurable provider environment variables for extraction, retrieval, and semantic drift
- persisted GitHub import jobs with `full` and `since_last_sync` modes
- dashboard visibility into demo repo and latest import result
- demo-oriented homepage and review queue improvements
- deployment documentation for a public single-machine demo

## Supported in v0.2

- one public demo workspace
- token-based GitHub import
- citation-first why answers
- rule-first drift plus conservative semantic drift
- CI-safe fake provider fallback when live credentials are missing

## Known limits

- no GitHub App auth
- no private-repo access control
- no multi-user login or roles
- no multi-workspace SaaS flow
- semantic drift remains conservative and intentionally narrow

## Deferred to v0.3

- GitHub App and webhook-based sync
- private repo support
- auth and permission layers
- multi-workspace operations
