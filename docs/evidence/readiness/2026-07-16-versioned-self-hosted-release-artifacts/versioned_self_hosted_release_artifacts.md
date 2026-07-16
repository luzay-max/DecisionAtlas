# Self-Hosted Release Artifact Verification

- Status: `pass`
- Version: `0.4.0-artifact-preview`
- Commit: `3cc30a2c783073c7d2d62b389ef8c50cf4628119`
- Proof level: `independent_runner_release_artifact`
- Customer controlled: `false`
- Blockers: `0`

## Checks

| Check | Status | Details |
| --- | --- | --- |
| Release artifact manifest is readable | pass | `{"path": "release-artifacts.json"}` |
| SHA256SUMS is well formed | pass | `{"entry_count": 4}` |
| Release manifest identity is valid | pass | `{"version": "0.4.0-artifact-preview"}` |
| Archive root is versioned and safe | pass | `{"value": "decisionatlas-self-hosted-0.4.0-artifact-preview"}` |
| Required release artifact kinds are listed | pass | `{"kinds": ["cyclonedx_sbom", "tar_gz", "zip"]}` |
| Artifact cyclonedx_sbom hash and size match | pass | `{"filename": "decisionatlas-self-hosted-0.4.0-artifact-preview.cdx.json", "size": 62730}` |
| Artifact tar_gz hash and size match | pass | `{"filename": "decisionatlas-self-hosted-0.4.0-artifact-preview.tar.gz", "size": 382920}` |
| Artifact zip hash and size match | pass | `{"filename": "decisionatlas-self-hosted-0.4.0-artifact-preview.zip", "size": 537321}` |
| Checksums cover exactly the release artifacts | pass | `{"files": ["decisionatlas-self-hosted-0.4.0-artifact-preview.cdx.json", "decisionatlas-self-hosted-0.4.0-artifact-preview.tar.gz", "decisionatlas-self-hosted-0.4.0-artifact-preview.zip", "release-artifacts.json"]}` |
| CycloneDX SBOM is readable | pass | `{"path": "decisionatlas-self-hosted-0.4.0-artifact-preview.cdx.json"}` |
| CycloneDX SBOM structure is valid | pass | `{"component_count": 311}` |
| ZIP members are safe | pass | `{"member_count": 278}` |
| tar.gz members are safe | pass | `{"member_count": 278}` |
| ZIP and tar.gz contain identical members | pass | `{"member_count": 278}` |
| Archive member counts and uncompressed sizes match the release manifest | pass | `{"file_count": 278, "uncompressed_size": 1728618}` |
| Extracted zip package content matches manifest | pass | `{"file_count": 278}` |
| Extracted zip package passes verifier | pass | `{"checked_file_count": 278}` |
| Extracted tar_gz package content matches manifest | pass | `{"file_count": 278}` |
| Extracted tar_gz package passes verifier | pass | `{"checked_file_count": 278}` |
| Verified ZIP was safely extracted to the operator-selected directory | pass | `{"package_root": "<operator-selected>/decisionatlas-self-hosted-0.4.0-artifact-preview"}` |

## Boundaries

- SHA-256 does not authenticate the publisher; cryptographic signing is not provided.
- Independent release-artifact verification is not customer-controlled-host installation proof.
