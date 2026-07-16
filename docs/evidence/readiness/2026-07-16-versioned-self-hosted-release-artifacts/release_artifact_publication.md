# Self-Hosted Release Artifact Publication

- Status: `pass`
- Version: `0.4.0-artifact-preview`
- Commit: `3cc30a2c783073c7d2d62b389ef8c50cf4628119`
- Package content SHA-256: `8bba734e99aea01fe11c484bf50c1907c9166eaade9714224112861f51e8112f`
- Proof level: `release_artifact_publication`
- Customer controlled: `false`

## Artifacts

| Kind | Filename | Size | SHA-256 |
| --- | --- | ---: | --- |
| zip | `decisionatlas-self-hosted-0.4.0-artifact-preview.zip` | 537321 | `e8144755709f5e22eaab1cf4e743db17ebd5f1f95d0efd41ddcb90fb122b6b25` |
| tar_gz | `decisionatlas-self-hosted-0.4.0-artifact-preview.tar.gz` | 382920 | `212b26f1ca719a337dc1054c5b1f64979ddcebdc57754f4728ae59406eade125` |
| cyclonedx_sbom | `decisionatlas-self-hosted-0.4.0-artifact-preview.cdx.json` | 62730 | `c0b228046f68f75169e3e0cc7ff25bc988657d333748df3f1abc309bfa0def9a` |

## SBOM

- Components: `311`
- npm: `278`
- PyPI: `33`

## Boundaries

- SHA-256 checks integrity relative to a trusted manifest source; cryptographic signing is not provided.
- The SBOM covers locked Node and Python dependencies, not OS packages, container images, runtime plugins, or vulnerability analysis.
- Archives do not include dependency caches; installation needs network access or an operator-supplied approved cache.
- Independent publication evidence is not customer-controlled-host installation proof.
