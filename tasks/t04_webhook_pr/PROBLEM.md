# Review and repair a defective webhook-delivery pull request

## Context

A teammate opened a pull request that adds outgoing webhooks: request signing, a
`verify()` helper for our own receivers, and delivery with retries. It is already merged
into your working copy (`repo/`). CI is green and the happy path works, but the on-call
engineer is nervous about it. The PR text and its diff are in `pr/` (`DESCRIPTION.md`,
`pr.diff`). The intended behavior is the contract in the docstrings of
`hooks/delivery.py` and `hooks/signing.py`, plus the PR description.

## Your task (two deliverables)

1. **Review.** Write `review.json` listing every defect you find:

   ```json
   {"findings": [
     {"file": "hooks/signing.py", "line": 30, "category": "security",
      "summary": "one sentence on what is wrong and why it matters"}
   ]}
   ```

   - `line` is a line number in the file as it is in `repo/` (the new-file side of the diff).
   - `category` is one of `security`, `correctness`, `reliability`, `error-handling`,
     `state`, `performance`.
   - One finding per distinct defect. Findings that are not real defects count against
     precision, and one comment covering two defects only finds one of them.

2. **Fix.** Produce a patch (unified diff relative to `repo/`) that repairs the defects
   without changing the public API.

## Grading

- The patch is graded by tests in the sandbox. Tests named `test_defect_NN_*` are grouped
  per defect, so the report says how many of the defects you resolved.
- `review.json` is graded separately and deterministically by matching file and line
  against a hidden list of known defects: recall, precision, F1.

```bash
codeforge run t04_webhook_pr --patch my_fix.patch
codeforge grade-review t04_webhook_pr review.json
```

## Notes

- No network access is available to tests; a fake transport is injected.
- Do not edit the tests; they live outside `repo/`.
