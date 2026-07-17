# Offline Dependency Bundle Verification

- Status: `pass`
- Package: `0.4.0-offline-dependencies`
- Commit: `fa420c5`
- Payload files: `17676`
- Payload size: `1679735721`
- Proof level: `offline_dependency_bundle_verified`
- Customer controlled: `false`

## Checks

| Check | Status |
| --- | --- |
| Selected package passes verifier | `pass` |
| Bundle paths are safe | `pass` |
| Bundle manifest is readable | `pass` |
| Bundle SBOM is readable | `pass` |
| SHA256SUMS is readable | `pass` |
| Bundle manifest identity is valid | `pass` |
| Checksums cover exactly every retained file | `pass` |
| Payload inventory matches manifest | `pass` |
| All approved cache categories are present | `pass` |
| Bundle is bound to selected package | `pass` |
| Consumer platform matches bundle | `pass` |
| CycloneDX SBOM is valid | `pass` |

## Boundaries

- Process-enforced offline installation is not physical air-gap or customer-controlled-host proof.
- Checksums do not authenticate the publisher; signing and vulnerability analysis are not provided.
