## 1. Public Reachability Probe

- [x] 1.1 Add bounded Git smart-HTTP public reachability probe to GitHubClient
- [x] 1.2 Use public probe fallback during public repository preflight
- [x] 1.3 Preserve credential-required versus provider/network failure classification

## 2. Verification

- [x] 2.1 Add GitHub client tests for public, private, and transient probe outcomes
- [x] 2.2 Add import preflight tests for rate-limit fallback and failed fallback classification
- [x] 2.3 Run focused and full engine tests plus OpenSpec strict validation
- [ ] 2.4 Push the fix and verify the failed GitHub Actions browser flow passes

## 3. Delivery

- [x] 3.1 Record the CI failure and fix in the dated update log and taskbook
- [ ] 3.2 Sync specs, archive the change, and create a scoped commit
