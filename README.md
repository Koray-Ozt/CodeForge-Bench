# CodeForge Bench

A compact software-engineering evaluation benchmark. It contains five realistic Python
engineering tasks, each with a verified reference solution, and a small CLI that applies a
**candidate patch** (human or AI-generated) to a task, runs the tests inside a
resource-limited Docker container, and writes a structured JSON and Markdown report.

It is built to demonstrate the skills behind AI coding-model evaluation: debugging,
performance work, refactoring, code review, test design, and judging whether a patch is
*actually* correct rather than merely plausible.

- Python 3.12+, pytest, ruff, Docker, GitHub Actions. No paid APIs, no frontend, no frameworks.
- Every result in this repository was produced by running the code; nothing is estimated.

## At a glance: a sample evaluation

The same runner scores any patch. Below, five patches for the code-review task
`t04_webhook_pr`, as produced by `codeforge verify` (copied from `results/verify.md`).
The last two are hand-written plausible-but-wrong fixes; no model was run.

| Patch | Status | Tests passed | Defects resolved |
|---|---|---|---|
| none (the defective PR as merged) | failed_tests | 16 / 29 | 0 / 9 |
| reference solution | **passed** | 29 / 29 | 9 / 9 |
| `naive_quick_fixes` (`compare_digest` on `str`, loop bound) | failed_tests | 16 / 29 | 2 / 9 |
| `fix_keeps_broad_except` (still catches `Exception`) | failed_tests | 28 / 29 | 8 / 9 |

The 8/9 patch fails one hidden test and would pass most reviews at a glance. That gap is
what this benchmark measures. Across all five tasks, 21 of 21 checks hold: every baseline
fails, every reference passes, and every wrong candidate is caught. Full tables:
[`results/verify.md`](results/verify.md). Everything runs in a network-less, memory- and
CPU-limited Docker container.

## Contents

1. [Quick start](#quick-start)
2. [The five tasks](#the-five-tasks)
3. [Benchmark design](#benchmark-design)
4. [Evaluation pipeline](#evaluation-pipeline)
5. [Sandbox and its limits](#sandbox-and-its-limits)
6. [Test strategy](#test-strategy)
7. [Performance measurement](#performance-measurement)
8. [Reports](#reports)
9. [Evaluating AI-generated patches](#evaluating-ai-generated-patches)
10. [Limitations and threats to validity](#limitations-and-threats-to-validity)
11. [Repository layout and development](#repository-layout-and-development)

## Quick start

Requirements: Python 3.12+, Docker (Desktop or Engine).

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
codeforge build-image                                   # one-off, builds codeforge-runner:1
codeforge list
codeforge show t01_inventory_race                       # the problem statement a candidate sees
```

Prove that every task is sound (baseline fails, reference passes, wrong candidates fail):

```bash
codeforge verify --all
```

Evaluate a patch (unified diff relative to the task's `repo/`):

```bash
codeforge run t01_inventory_race --patch tasks/t01_inventory_race/reference/solution.patch
codeforge run t01_inventory_race --patch my_fix.patch --out runs   # writes runs/t01_inventory_race.{json,md}
```

Other commands:

```bash
codeforge bench t02_ledger_reconcile                    # before/after timings -> results/
codeforge grade-review t04_webhook_pr review.json       # score a code review
pytest -m "not docker"                                   # runner unit tests, no Docker
pytest -m docker                                         # hostile-patch sandbox tests
ruff check . && ruff format --check .
```

## The five tasks

None of these is a puzzle with a one-line answer. Each is a small production-shaped
codebase where the obvious fix is incomplete, and where a plausible patch can pass the
visible tests and still be wrong.

| # | Task | Category | The situation | Why the obvious fix fails |
|---|---|---|---|---|
| 1 | `t01_inventory_race` | race condition | Stock reservation service sells the last unit twice, double-credits returns, and sells units it also returns | A global lock fixes overselling but serializes every SKU (requirement 3); locking only `reserve` leaves release/confirm/sweep races |
| 2 | `t02_ledger_reconcile` | performance | Month-end reconciliation of bank lines against ledger entries is quadratic; 20k x 20k times out | Swapping a list for a set is faster but still quadratic; a fast bucketed rewrite that drops the "reference hit first" tie-break changes results |
| 3 | `t03_pricing_legacy` | refactoring | A 123-line, complexity-42 pricing function; two business changes queued behind it | Adding the changes in place passes behavior tests and fails the maintainability gate; "simplifying" banker's rounding to half-up changes cents on historic invoices |
| 4 | `t04_webhook_pr` | code review | A merged PR adds signed, retrying webhooks; nine defects hide on failure paths | Quick fixes such as `hmac.compare_digest(str, str)` crash on non-ASCII input; a fix that still catches `Exception` leaves a defect |
| 5 | `t05_orders_api` | backend feature | Cursor pagination, idempotency keys and optimistic locking for a stdlib WSGI/SQLite API with existing databases | `OFFSET` cursors skip rows; `SELECT`-then-`INSERT` races; forgetting to migrate existing databases |

Each task directory contains:

```
PROBLEM.md                 what the candidate sees (context, requirements, constraints)
repo/                      the starting codebase (the candidate's patch is relative to it)
tests/                     visible regression tests (shown to the candidate)
hidden_tests/              edge cases, only run at evaluation time
reference/solution.patch   verified reference solution
reference/EXPLANATION.md   root cause, fix, rejected alternatives, residual risk
candidates/                hand-written plausible-but-wrong patches, each with an expected outcome
task.toml                  limits, scoring, benchmark settings
```

Read the `reference/EXPLANATION.md` files first; they are the technical write-ups.

## Benchmark design

**A patch is the unit of evaluation.** The runner is agnostic to who wrote the diff.

**Baseline fails, reference passes, wrong candidates fail.** `codeforge verify` enforces,
for every task and on every CI run:

1. the unmodified baseline fails at least one test *by assertion* (not by crashing) while
   still passing others, so the suite tests behavior and not just importability;
2. the reference patch passes everything;
3. every shipped candidate patch yields exactly its declared outcome.

The candidates are the most important part. They encode the failure modes that a
text-matching or "does it run" evaluation would miss. Examples that the tests catch: a
global lock (fails the different-SKU concurrency test and nothing else), a fast rewrite that
drops a tie-break rule (passes the scaling test, fails differential tests), a
clean-looking refactor with changed rounding (fails 40 of 656 tests, all golden cases).

**Visible versus hidden tests.** The candidate sees `tests/`; `hidden_tests/` is copied into
the container only after the patch is applied. This measures generalization to the
requirements rather than fitting to the visible assertions.

**Partial credit that means something.** Beyond pass/fail the report gives per-test
results, a score (fraction of tests passed), and, for the review task, a per-defect
breakdown (`Defects resolved: 8/9 (unresolved: 08)`). Code review is graded separately and
deterministically with `grade-review` (recall, precision, F1; no LLM judge).

**Determinism over timing.** No test uses `sleep` to order events or relies on wall-clock
speed as the primary signal. See [Test strategy](#test-strategy).

## Evaluation pipeline

```
 candidate.patch
      |
      v
 host: static checks  (size, UTF-8, no ../ or absolute paths, no symlinks/binary,
      |                no edits to tests/, conftest.py, pytest.ini, pyproject.toml, *.pth ...)
      v                                  -> status "patch_rejected" if any check fails
 host: stage isolated copies  repo/ , tests/ , bench/ , candidate.patch   (temp dir)
      |
      v
 docker run  --network none --memory --cpus --pids-limit --cap-drop ALL --read-only ...
   |  1. cp repo into a tmpfs, `git apply` the patch   -> exit 10 => "patch_rejected"
   |  2. copy tests into /work/_cf_tests (outside the repo, after patching)
   |  3. pytest --junitxml=/out/junit.xml
      |
      v
 host: kill on timeout, read OOM flag, parse junit.xml (size-capped)
      |
      v
 status in { passed, failed_tests, patch_rejected, timeout, oom, infra_error }
 + per-test outcomes, defect grouping, limits used, image id, patch sha256
      |
      v
 report.json + report.md
```

Key decisions:

- **The candidate patch is never applied or executed on the host.** The host only reads it
  as bytes and runs regex checks; `git apply` and the tests run inside the container.
- **Tests are copied in after patching and live outside the repo**, so a patch cannot ship
  a `conftest.py` that is collected alongside them, and edits to test infrastructure are
  rejected up front.
- **Distinct statuses** separate "the code is wrong" (`failed_tests`) from "the patch does
  not apply" (`patch_rejected`), "it hangs" (`timeout`), "it blows memory" (`oom`) and "our
  harness broke" (`infra_error`), because they mean different things when comparing models.

## Sandbox and its limits

Every container is started with:

| Control | Setting |
|---|---|
| Network | `--network none` |
| Memory | `--memory` and `--memory-swap` equal (no swap), per task (256 MB default) |
| CPU | `--cpus` (1 by default) |
| Processes | `--pids-limit` (64-128), stops fork bombs |
| Privileges | `--cap-drop ALL`, `--security-opt no-new-privileges`, non-root uid 1000 |
| Filesystem | `--read-only` root; writable tmpfs for `/work` (64 MB) and `/tmp` (32 MB) only |
| Inputs | mounted read-only at `/in`; only `/out` (results) is writable on the host |
| Time | wall-clock timeout; the container is killed and removed |
| Output | per-file write cap via `ulimit -f`; host keeps only the last 4 KB of the log |

`tests/test_sandbox_isolation.py` (`pytest -m docker`) runs hostile patches through the real
runner and asserts these controls hold: unreachable network, non-root user, read-only
filesystem, no host paths visible, pid limit enforced, memory bomb killed, infinite loop
timed out, output flood bounded.

**What this does not give you. Do not treat this as a hardened sandbox.**

- Containers **share the host kernel**. A kernel or container-runtime vulnerability is an
  escape. For adversarial code use gVisor, Kata Containers or Firecracker, ideally on a
  disposable VM.
- The `/out` bind mount is writable by the candidate's code. A patch can **forge
  `junit.xml`** (it runs in the same process as pytest). Static patch checks and the
  per-test failure messages help, but results from untrusted patches should be
  spot-checked, or the test run should be moved out of the candidate's process.
- Disk is bounded only through tmpfs sizes and `ulimit -f`; many small files on `/out`
  are not capped.
- Docker's default seccomp and AppArmor profiles are used as shipped; no custom profile.
- On Docker Desktop (Windows/macOS) the daemon runs inside a VM, which adds a layer but
  also means limits are enforced by that VM's kernel.
- Time limits are wall-clock; CPU time and wall time differ under contention.
- A candidate can still special-case the visible tests or detect the harness. Hidden tests
  reduce but do not remove this.
- `codeforge` itself runs on your host with your privileges and trusts the task
  directories. Only evaluate task packs you wrote or reviewed.

## Test strategy

Each task uses the cheapest technique that is **deterministic**.

| Problem | Technique |
|---|---|
| Race conditions (t01) | A store wrapper calls a hook while a `get` reply is "in flight". A one-shot barrier in the hook lines threads up so a check-then-act race happens on every run. A correct fix serializes the threads, the barrier times out, and the test still passes: only the final state is asserted. Re-entrant hooks that spawn a helper thread exercise confirm-versus-release interleavings. A stress test is a *backstop*, not the detector. |
| Performance (t02) | (1) Differential tests against a deliberately naive oracle on 450 dense, collision-heavy inputs plus realistic workloads. (2) Complexity measured by **executed-line counts** via `sys.monitoring`: quadrupling the input must not multiply work by more than 7 (linear is ~4, quadratic ~16). Machine-independent. (3) A coarse wall-clock budget in a child process with a hard kill, as a backstop for work done in C. |
| Refactoring (t03) | Golden master: inputs and outputs recorded by running the **original** code (36 hand-picked scenarios, 600 seeded random orders). AST-based gates for cyclomatic complexity and function length. New behavior checked with hand-computed expectations. |
| Review (t04) | One test per defect (`test_defect_NN_*`), grouped in the report. Includes tests that block *naive fixes*, such as non-ASCII signatures that crash `compare_digest(str, str)`. Review text is graded by file/line matching. |
| Backend (t05) | In-process WSGI client against a real SQLite file. Deterministic discriminators (offset-vs-keyset under filter changes, legacy-database upgrade, error precedence) plus thread-based races for idempotency and optimistic locking. |

Flakiness is treated as a defect: the concurrency tests were run repeatedly against the
reference solution. The idempotency and optimistic-locking race tests (t05) are
probabilistic against a *wrong* implementation (a racy check-then-act can occasionally
survive a run) but never fail a correct one.

## Performance measurement

`codeforge bench t02_ledger_reconcile` runs `tasks/t02_ledger_reconcile/bench/bench_reconcile.py`
twice in the same sandbox settings (baseline, then with the reference patch). Each case does
1 untimed warm-up and 5 timed repeats with `time.perf_counter`, and records a **digest of the
output**; the report refuses to print a speedup if baseline and reference outputs differ.

Results from the last run on the author's machine (12th Gen Intel Core i5-12450H, 12
logical CPUs, Docker Desktop on WSL2 with 3.9 GB for the VM, container limited to
`--cpus 1 --memory 256m`, Python 3.12). Raw data: `results/t02_ledger_reconcile_bench.json`.

| Case | Baseline median (s) | Reference median (s) | Speedup | Baseline IQR | Reference IQR | Output digest |
|---|---|---|---|---|---|---|
| 2000x2000 | 0.1314 | 0.0020 | 66.6x | 0.0135 | 0.0001 | `ce1c091394e97a16` (identical) |
| 5000x5000 | 0.8643 | 0.0058 | 148.0x | 0.0116 | 0.0006 | `51780825167910ce` (identical) |
| 10000x10000 | 3.6893 | 0.0117 | 315.9x | 0.0559 | 0.0013 | `24823736bf8deda1` (identical) |

How to read this and what it does not show:

- The speedup grows with input size because the baseline is quadratic and the reference is
  close to linear. It is a property of the algorithm on this workload, not a general claim.
- Absolute numbers depend on the machine. I ran the benchmark four times while developing;
  the speedup ranged 67-80x (2000), 142-154x (5000) and 213-316x (10000). The 10000-case
  range is wide because the reference takes only ~12-18 ms, so small absolute noise moves
  the ratio a lot. Quote the baseline and reference times, not just the ratio, and rerun
  it yourself.
- Medians and inter-quartile ranges of only 5 repeats are indicative, not statistically
  rigorous. There is no confidence interval.
- Docker on Windows runs in a VM, so timer resolution, CPU frequency scaling, thermal state
  and other host load all add noise. `--cpus 1` is a CFS quota, not a pinned core.
- One synthetic workload with a fixed seed. Real data with heavy skew (very many identical
  amounts on one day) would behave differently; `reference/EXPLANATION.md` discusses that
  degenerate case.
- Python start-up, import time and GC are excluded; only the call is timed.
- This is why correctness of the optimization is **not** judged by time: the task's tests
  use differential testing and line-count scaling.

## Reports

`codeforge run` and `codeforge verify --out DIR` write JSON and Markdown. The JSON schema
(abridged, copied from `results/verify.json`; the `environment` block also records
codeforge and Python versions, host OS and a timestamp):

```json
{
  "environment": {"codeforge": "0.1.0", "python": "3.12.0", "host_os": "...", "generated_at": "..."},
  "results": [{
    "task_id": "t04_webhook_pr",
    "label": "candidate:candidates/fix_keeps_broad_except.patch",
    "status": "failed_tests",
    "exit_code": 1,
    "duration_s": 0.656,
    "patch_sha256": "22717e1aa475927ed1b3fceccd1602b9aef491e1b6b677bcd2c203eeb39cf172",
    "limits": {"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 120, "network": "none"},
    "image_id": "sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5",
    "defects": {"total": 9, "resolved": 8, "unresolved": ["08"]},
    "summary": {"total": 29, "passed": 28, "failed": 1, "error": 0, "skipped": 0, "score": 0.9655},
    "tests": [{"name": "hidden.test_delivery_defects::test_defect_08_programming_errors_are_not_swallowed_or_retried",
               "outcome": "failed", "duration_s": 0.0,
               "message": "hooks.delivery.DeliveryFailed: delivery failed after 5 attempt(s): bug in transp..."}],
    "detail": "", "output_tail": ""
  }]
}
```

`results/verify.{json,md}` is the report of the last full `verify --all` run.

## Evaluating AI-generated patches

The harness is model-agnostic and needs no API: produce a unified diff however you like
and run it.

```bash
codeforge show t05_orders_api > prompt.md       # give this and the repo/ contents to a model
# ... get a diff back, save as model_patch.diff ...
codeforge run t05_orders_api --patch model_patch.diff --label some-model --out runs/some-model
```

What to look at beyond the status line:

- `patch_rejected` with a reason (path escape, protected file) versus a real `git apply`
  failure (malformed or stale diff). Models often fail the second way.
- Which *hidden* tests fail while the visible ones pass: that gap is overfitting to the
  visible tests.
- The per-defect breakdown on t04 and the `grade-review` F1 on a `review.json`: fixing
  and spotting are different skills.
- The `candidates/` directory documents the failure modes worth looking for in model output:
  scope-limited locks, speedups that change semantics, refactors that change numbers, fixes
  that crash on unusual input, features that work only on fresh databases.

## Limitations and threats to validity

- **Five tasks is a demonstration, not a statistically meaningful benchmark.** Scores on it
  cannot rank models.
- **Contamination.** The tasks are public. A model that has seen this repository can
  reproduce the reference solutions.
- **Hidden tests are hidden only by convention.** The harness assumes the candidate is
  shown `PROBLEM.md`, `repo/` and `tests/`, not the whole task directory.
- **Tests encode one reading of the requirements.** I tried to make requirements explicit in
  `PROBLEM.md`, but alternative valid designs may fail an over-specific assertion (for
  example t01's use of a store `get`/`set` contract, or t05's replay semantics, which are
  stated in the problem).
- **Differential tests are only as good as the oracle**, and golden masters only cover the
  sampled input space. Both are described in each task's `EXPLANATION.md`.
- **Probabilistic race tests** (t05 idempotency/locking) can in rare cases pass a wrong
  implementation; the deterministic discriminators in the same suites are the primary
  signal.
- **Result integrity.** See [Sandbox and its limits](#sandbox-and-its-limits): a malicious
  patch can forge the JUnit file. This is acceptable for cooperative or model-generated
  patches and must be hardened for adversarial use.
- **Hand-written candidates are my guesses about failure modes**, not measured model
  outputs. No model was run against these tasks in this repository.
- **CI** is configured (`.github/workflows/ci.yml`), but its Docker job could only be
  validated here by running the same commands locally on Windows with Docker Desktop.
- **Python only**, a single interpreter version, no dependency installs (offline sandbox).

## Repository layout and development

```
src/codeforge/      cli.py task.py patching.py sandbox.py runner.py results.py
                    report.py verify.py review.py bench.py
docker/             Dockerfile.runner, entrypoint.sh (runs inside the container)
scripts/            make_patch.sh   maintainer tool: diff a task repo against a modified copy
tasks/              the five tasks (see above)
tests/              unit tests for the runner + sandbox isolation tests (-m docker)
results/            generated verify and benchmark reports
.github/workflows/  ci.yml
```

Adding a task: create `tasks/tNN_name/` with `task.toml`, `PROBLEM.md`, `repo/`, `tests/`,
`hidden_tests/` and `reference/solution.patch` (generate it with `scripts/make_patch.sh`),
add at least one wrong candidate, then run `codeforge verify tNN_name`.
`tests/test_tasks.py` enforces the structure.

The runner image is built from `python:3.12-slim` with a pinned pytest; rebuild it with
`codeforge build-image` after changing `docker/`.

## License

MIT, see [LICENSE](LICENSE).
