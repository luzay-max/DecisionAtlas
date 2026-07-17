# Offline Dependency Bundle Preparation

- Status: `pass`
- Package: `0.4.0-offline-dependencies`
- Commit: `fa420c5`
- Proof level: `offline_dependency_bundle_prepared`
- Customer controlled: `false`

## Categories

| Category | Files | Size |
| --- | ---: | ---: |
| container_images | 1 | 490422272 |
| playwright_browsers | 610 | 686538373 |
| pnpm_store | 14699 | 458675797 |
| uv_cache | 2366 | 44099279 |

## Blockers

- None

## Boundaries

- Tool-native caches are platform and toolchain specific.
- Process-enforced offline installation is not physical air-gap or customer-host proof.
- Signing and vulnerability analysis are not provided.
