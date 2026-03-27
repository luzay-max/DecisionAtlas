# 2026-03-27 Why-Search Support Validation

## Scope

Validated imported why-search behavior after the `add-why-answer-support-grading` change against the live imported workspace for `n8n-io/n8n`.

## Test Cases

### Case 1

Question:

`为什么发布候选分支操作要改用 GitHub App token？`

Observed result:

- Status: `部分支撑`
- Primary decision matched correctly:
  - `Use GitHub App token for release candidate branch operations`
- Answer stayed focused on the matched decision.
- Only one grounded citation was shown.

Assessment:

- Expected behavior.
- Confirms the system no longer collapses "correct answer with one citation" into `证据不足`.
- Confirms the earlier why-focus work still prevents adjacent release decisions from being blended into the main answer.

### Case 2

Question:

`为什么要把 variables.value 从 varchar(255) 扩到 1000 字符？`

Observed result:

- Status: `部分支撑`
- Primary decision matched correctly:
  - `Add migration to expand variables.value column from varchar(255) to support 1,000 characters`
- Answer stayed focused on the matched decision.
- Only one grounded citation was shown.

Assessment:

- Expected behavior.
- Confirms `limited_support` is not a single-case fix and is applied consistently to another imported decision.

## Conclusion

The new support grading works as intended:

- `why-search focus` is holding
- `limited_support` now correctly represents partially grounded answers
- imported why answers are no longer mislabeled as outright failures when one grounded citation exists

## Current Bottleneck

The dominant limitation is now `source ref coverage`, not why-answer focus:

- correct primary decisions are being selected
- answers are staying focused
- but accepted decisions frequently expose only one usable grounded citation

This means more imported why results are landing in `limited_support` instead of `ok`.

## Recommended Next Step

Prioritize a change focused on improving `source ref coverage` for accepted decisions so more imported why answers can move from:

`limited_support -> ok`
