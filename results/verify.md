# CodeForge Bench report

Generated 2026-11-03T02:12:49+00:00 on `Windows-11-10.0.26200-SP0` (codeforge 0.1.0).

| Task | Run | Status | Passed | Failed | Error | Score | Time (s) |
|---|---|---|---|---|---|---|---|
| t01_inventory_race | baseline | **failed_tests** | 11 | 6 | 0 | 0.65 | 0.7 |
| t01_inventory_race | reference | **passed** | 17 | 0 | 0 | 1.00 | 1.6 |
| t01_inventory_race | candidate:candidates/global_lock.patch | **failed_tests** | 16 | 1 | 0 | 0.94 | 4.2 |
| t01_inventory_race | candidate:candidates/lock_reserve_only.patch | **failed_tests** | 12 | 5 | 0 | 0.71 | 3.2 |
| t02_ledger_reconcile | baseline | **failed_tests** | 464 | 2 | 0 | 1.00 | 11.8 |
| t02_ledger_reconcile | reference | **passed** | 466 | 0 | 0 | 1.00 | 1.7 |
| t02_ledger_reconcile | candidate:candidates/set_for_matched_ids.patch | **failed_tests** | 464 | 2 | 0 | 1.00 | 11.7 |
| t02_ledger_reconcile | candidate:candidates/drops_reference_rule.patch | **failed_tests** | 160 | 306 | 0 | 0.34 | 3.1 |
| t03_pricing_legacy | baseline | **failed_tests** | 646 | 10 | 0 | 0.98 | 1.9 |
| t03_pricing_legacy | reference | **passed** | 656 | 0 | 0 | 1.00 | 1.7 |
| t03_pricing_legacy | candidate:candidates/patch_in_place.patch | **failed_tests** | 655 | 1 | 0 | 1.00 | 1.4 |
| t03_pricing_legacy | candidate:candidates/refactor_changes_rounding.patch | **failed_tests** | 616 | 40 | 0 | 0.94 | 1.5 |
| t04_webhook_pr | baseline | **failed_tests** | 16 | 13 | 0 | 0.55 | 0.8 |
| t04_webhook_pr | reference | **passed** | 29 | 0 | 0 | 1.00 | 0.7 |
| t04_webhook_pr | candidate:candidates/naive_quick_fixes.patch | **failed_tests** | 16 | 13 | 0 | 0.55 | 0.8 |
| t04_webhook_pr | candidate:candidates/fix_keeps_broad_except.patch | **failed_tests** | 28 | 1 | 0 | 0.97 | 1.1 |
| t05_orders_api | baseline | **failed_tests** | 18 | 42 | 0 | 0.30 | 2.0 |
| t05_orders_api | reference | **passed** | 60 | 0 | 0 | 1.00 | 2.1 |
| t05_orders_api | candidate:candidates/offset_cursor_and_check_then_insert.patch | **failed_tests** | 57 | 3 | 0 | 0.95 | 1.4 |
| t05_orders_api | candidate:candidates/no_in_place_migration.patch | **failed_tests** | 59 | 1 | 0 | 0.98 | 1.4 |

## t01_inventory_race / baseline

- Limits: `{"memory": "256m", "cpus": "1", "pids": 128, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`

Failing tests:

- `hidden.test_concurrency_edges::test_double_release_credits_units_once` (failed): AssertionError: [KeyError('e48530335fc042a5bb6cf2476d185822'), True]
- `hidden.test_concurrency_edges::test_release_and_reserve_do_not_lose_updates` (failed): AssertionError: assert 10 == 8
- `hidden.test_concurrency_edges::test_confirm_racing_with_release_or_sweep_is_exclusive[release]` (failed): KeyError: '50109e1a35f64efaab686be67cbf69c1'
- `hidden.test_concurrency_edges::test_confirm_racing_with_release_or_sweep_is_exclusive[sweep]` (failed): KeyError: 'f09a486ef43548a5b0c914e36bba3bec'
- `hidden.test_concurrency_edges::test_stress_invariants_hold` (failed): AssertionError: A
- `visible.test_service::test_concurrent_reserves_do_not_oversell` (failed): AssertionError: [Reservation(id='199fa7596b5640b592118e14a8bcccd2', sku='LAST', quantity=1, holder='alice', expires_at=1060.0), Reservation(id='3e27372bee30496093a77588fd05f683', sku='LAST', quantity=1, holder='bob', expires_at=1060.0)]

## t01_inventory_race / reference

- Limits: `{"memory": "256m", "cpus": "1", "pids": 128, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `b6c4302694e85c93a8a58d016c91987f027f2e7f599f7c558e5f152c12cf6d7b`

## t01_inventory_race / candidate:candidates/global_lock.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 128, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `68b35380dce350807528b47af1e27d812a5d2d6cf69442f00691539fbf3ff79d`

Failing tests:

- `hidden.test_concurrency_edges::test_different_skus_are_not_serialized` (failed): AssertionError: reservations for different SKUs never overlapped in the store

## t01_inventory_race / candidate:candidates/lock_reserve_only.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 128, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `949935e83ae1163c0a40b53cd6ac550f2689d02855a9a6475e4838a61a3468a8`

Failing tests:

- `hidden.test_concurrency_edges::test_double_release_credits_units_once` (failed): AssertionError: [KeyError('ace1107f4f92422897de5dbc11b91b75'), True]
- `hidden.test_concurrency_edges::test_release_and_reserve_do_not_lose_updates` (failed): AssertionError: assert 10 == 8
- `hidden.test_concurrency_edges::test_different_skus_are_not_serialized` (failed): AssertionError: reservations for different SKUs never overlapped in the store
- `hidden.test_concurrency_edges::test_confirm_racing_with_release_or_sweep_is_exclusive[release]` (failed): KeyError: 'deddf395ce474cb9ac74d6e3e4d14e57'
- `hidden.test_concurrency_edges::test_confirm_racing_with_release_or_sweep_is_exclusive[sweep]` (failed): KeyError: 'd00b439e1dca403e97e136c23c5fa89e'

## t02_ledger_reconcile / baseline

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 300, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`

Failing tests:

- `hidden.test_budget::test_twenty_thousand_by_twenty_thousand_within_budget` (failed): AssertionError: reconcile still running after 10s
- `visible.test_scaling::test_work_grows_near_linearly_with_input_size` (failed): AssertionError: 4x input caused 15.8x more executed lines (quadratic is ~16x)

## t02_ledger_reconcile / reference

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 300, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `ea3387fb667dd21d3ce6b2125d510c5a6dff768d33d3b2df377ed60549823092`

## t02_ledger_reconcile / candidate:candidates/set_for_matched_ids.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 300, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `4a46d01c1b8309100f0a31eebd2357d08b39b069e29b964d213cd4c50648982f`

Failing tests:

- `hidden.test_budget::test_twenty_thousand_by_twenty_thousand_within_budget` (failed): AssertionError: reconcile still running after 10s
- `visible.test_scaling::test_work_grows_near_linearly_with_input_size` (failed): AssertionError: 4x input caused 15.8x more executed lines (quadratic is ~16x)

## t02_ledger_reconcile / candidate:candidates/drops_reference_rule.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 300, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `6d073b57eb8c00a5bb2052eba9f462c7a70816bc94bed4b55437bc39bee41794`

Failing tests:

- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-0]` (failed): AssertionError: assert ([('T1', 'E2'...', 'E7', ...]) == ([('T1', 'E2'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-2]` (failed): AssertionError: assert ([('T5', 'E2'... ['E0', 'E1']) == ([('T5', 'E2'... ['E0', 'E1'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-5]` (failed): AssertionError: assert ([('T1', 'E19...', 'E6', ...]) == ([('T1', 'E19...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-6]` (failed): AssertionError: assert ([('T0', 'E16...', 'E9', ...]) == ([('T0', 'E16...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-11]` (failed): AssertionError: assert ([('T0', 'E27..., 'E10', ...]) == ([('T0', 'E27...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-13]` (failed): AssertionError: assert ([('T0', 'E4'...', 'E7', ...]) == ([('T0', 'E4'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-17]` (failed): AssertionError: assert ([('T0', 'E9'..., 'E10', ...]) == ([('T0', 'E9'...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-18]` (failed): AssertionError: assert ([('T1', 'E7'... 'E8', 'E10']) == ([('T1', 'E7'... 'E8', 'E10'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-20]` (failed): AssertionError: assert ([('T1', 'E1'..., 'E7', 'E8']) == ([('T1', 'E1'..., 'E7', 'E8'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-22]` (failed): AssertionError: assert ([('T5', 'E3'..., 'E5', 'E6']) == ([('T5', 'E3'..., 'E5', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-23]` (failed): AssertionError: assert ([('T0', 'E4'...', 'E6', ...]) == ([('T0', 'E4'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-24]` (failed): AssertionError: assert ([('T1', 'E4'...', 'E7', ...]) == ([('T1', 'E4'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-26]` (failed): AssertionError: assert ([('T3', 'E3'..., 'E10', ...]) == ([('T3', 'E3'..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-27]` (failed): AssertionError: assert ([('T0', 'E15...', 'E6', ...]) == ([('T0', 'E15...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-29]` (failed): AssertionError: assert ([('T2', 'E7'...', 'E8', ...]) == ([('T2', 'E7'...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-30]` (failed): AssertionError: assert ([('T0', 'E11...', 'E5', ...]) == ([('T0', 'E11...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-35]` (failed): AssertionError: assert ([('T1', 'E18...', 'E7', ...]) == ([('T1', 'E18...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-36]` (failed): AssertionError: assert ([('T3', 'E10...', 'E6', ...]) == ([('T3', 'E10...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-38]` (failed): AssertionError: assert ([('T1', 'E19...', 'E5', ...]) == ([('T1', 'E19...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-41]` (failed): AssertionError: assert ([('T1', 'E20...', 'E7', ...]) == ([('T1', 'E20...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-42]` (failed): AssertionError: assert ([('T4', 'E2'..., 'E5', 'E6']) == ([('T4', 'E2'..., 'E5', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-44]` (failed): AssertionError: assert ([('T1', 'E12...', 'E6', ...]) == ([('T1', 'E12...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-46]` (failed): AssertionError: assert ([('T14', 'E3... ...], ['E0']) == ([('T14', 'E3... ...], ['E0'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-48]` (failed): AssertionError: assert ([('T0', 'E9'...', 'E5', ...]) == ([('T0', 'E9'...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-51]` (failed): AssertionError: assert ([('T2', 'E10..., 'E11', ...]) == ([('T2', 'E10..., 'E11', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-52]` (failed): AssertionError: assert ([('T2', 'E1'...', 'E7', ...]) == ([('T2', 'E1'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-54]` (failed): AssertionError: assert ([('T5', 'E7'..., 'E2', 'E6']) == ([('T5', 'E7'..., 'E2', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-56]` (failed): AssertionError: assert ([('T4', 'E0'...', 'E8', ...]) == ([('T4', 'E0'...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-60]` (failed): AssertionError: assert ([('T3', 'E10...', 'E9', ...]) == ([('T3', 'E10...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-62]` (failed): AssertionError: assert ([('T1', 'E19...', 'E6', ...]) == ([('T1', 'E19...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-64]` (failed): AssertionError: assert ([('T0', 'E6'...', 'E8', ...]) == ([('T0', 'E13...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-65]` (failed): AssertionError: assert ([('T4', 'E22...', 'E5', ...]) == ([('T4', 'E22...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-66]` (failed): AssertionError: assert ([('T1', 'E2'... ['E0', 'E3']) == ([('T1', 'E2'... ['E0', 'E3'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-67]` (failed): AssertionError: assert ([('T1', 'E2'... ...], ['E0']) == ([('T1', 'E2'... ...], ['E0'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-68]` (failed): AssertionError: assert ([('T1', 'E17...', 'E8', ...]) == ([('T1', 'E17...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-74]` (failed): AssertionError: assert ([('T0', 'E4'...', 'E8', ...]) == ([('T0', 'E26...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-76]` (failed): AssertionError: assert ([('T0', 'E20...', 'E7', ...]) == ([('T0', 'E20...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-78]` (failed): AssertionError: assert ([('T4', 'E7'...', 'E6', ...]) == ([('T4', 'E7'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-79]` (failed): AssertionError: assert ([('T0', 'E2'...', 'E6', ...]) == ([('T0', 'E2'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-80]` (failed): AssertionError: assert ([('T3', 'E8'..., 'E14', ...]) == ([('T3', 'E8'..., 'E14', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-81]` (failed): AssertionError: assert ([('T0', 'E26...', 'E6', ...]) == ([('T0', 'E26...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-82]` (failed): AssertionError: assert ([('T5', 'E6'..., 'E7', 'E8']) == ([('T5', 'E6'..., 'E7', 'E8'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-88]` (failed): AssertionError: assert ([('T3', 'E9'..., 'E11', ...]) == ([('T3', 'E9'..., 'E11', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-89]` (failed): AssertionError: assert ([('T5', 'E3'..., 'E1', 'E4']) == ([('T5', 'E3'..., 'E1', 'E4'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-90]` (failed): AssertionError: assert ([('T3', 'E12...', 'E5', ...]) == ([('T3', 'E12...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-93]` (failed): AssertionError: assert ([('T2', 'E10...', 'E7', ...]) == ([('T2', 'E10...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-94]` (failed): AssertionError: assert ([('T8', 'E8'...', 'E6', ...]) == ([('T8', 'E8'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-95]` (failed): AssertionError: assert ([('T4', 'E17...', 'E8', ...]) == ([('T4', 'E17...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-101]` (failed): AssertionError: assert ([('T2', 'E3'...', 'E6', ...]) == ([('T2', 'E3'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-105]` (failed): AssertionError: assert ([('T2', 'E16...', 'E6', ...]) == ([('T2', 'E16...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-107]` (failed): AssertionError: assert ([('T2', 'E13...'E10', 'E12']) == ([('T2', 'E13...'E10', 'E12'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-108]` (failed): AssertionError: assert ([('T6', 'E2'..., 'E5', 'E6']) == ([('T6', 'E2'..., 'E5', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-110]` (failed): AssertionError: assert ([('T0', 'E19...', 'E6', ...]) == ([('T0', 'E19...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-111]` (failed): AssertionError: assert ([('T2', 'E7'...'E11', 'E12']) == ([('T2', 'E7'...'E11', 'E12'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-115]` (failed): AssertionError: assert ([('T0', 'E2'..., 'E12', ...]) == ([('T0', 'E2'..., 'E12', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-116]` (failed): AssertionError: assert ([('T2', 'E26...', 'E9', ...]) == ([('T2', 'E26...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-121]` (failed): AssertionError: assert ([('T8', 'E1'..., 'E3', 'E4']) == ([('T8', 'E1'..., 'E3', 'E4'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-122]` (failed): AssertionError: assert ([('T1', 'E14...', 'E7', ...]) == ([('T1', 'E14...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-124]` (failed): AssertionError: assert ([('T1', 'E6'..., 'E15', ...]) == ([('T1', 'E6'..., 'E15', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-125]` (failed): AssertionError: assert ([('T1', 'E2'...', 'E9', ...]) == ([('T1', 'E2'...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-127]` (failed): AssertionError: assert ([('T8', 'E1'...T5', ...], []) == ([('T8', 'E1'...T5', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-128]` (failed): AssertionError: assert ([('T3', 'E13..., 'E10', ...]) == ([('T3', 'E13..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-129]` (failed): AssertionError: assert ([('T0', 'E4'...', 'E6', ...]) == ([('T0', 'E4'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-131]` (failed): AssertionError: assert ([('T2', 'E19...', 'E5', ...]) == ([('T2', 'E19...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-132]` (failed): AssertionError: assert ([('T0', 'E8'...', 'E7', ...]) == ([('T0', 'E8'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-134]` (failed): AssertionError: assert ([('T2', 'E29...', 'E6', ...]) == ([('T2', 'E29...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-138]` (failed): AssertionError: assert ([('T3', 'E2'...'E10', 'E11']) == ([('T3', 'E2'...'E10', 'E11'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-141]` (failed): AssertionError: assert ([('T4', 'E29...', 'E6', ...]) == ([('T4', 'E29...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-142]` (failed): AssertionError: assert ([('T1', 'E14...', 'E5', ...]) == ([('T1', 'E14...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-143]` (failed): AssertionError: assert ([('T5', 'E5'..., 'E6', 'E7']) == ([('T5', 'E5'..., 'E6', 'E7'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-144]` (failed): AssertionError: assert ([('T1', 'E22...', 'E5', ...]) == ([('T1', 'E22...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-145]` (failed): AssertionError: assert ([('T2', 'E13...', 'E7', ...]) == ([('T2', 'E13...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-146]` (failed): AssertionError: assert ([('T6', 'E4'..., 'E5', 'E7']) == ([('T6', 'E4'..., 'E5', 'E7'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-147]` (failed): AssertionError: assert ([('T1', 'E16...', 'E9', ...]) == ([('T1', 'E19...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[0-148]` (failed): AssertionError: assert ([('T4', 'E19...', 'E8', ...]) == ([('T4', 'E19...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-0]` (failed): AssertionError: assert ([('T1', 'E2'..., 'E15', ...]) == ([('T1', 'E2'..., 'E15', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-1]` (failed): AssertionError: assert ([('T1', 'E4'... ['E1', 'E6']) == ([('T1', 'E4'... ['E1', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-2]` (failed): AssertionError: assert ([('T5', 'E2'... ['E0', 'E1']) == ([('T5', 'E2'... ['E0', 'E1'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-5]` (failed): AssertionError: assert ([('T1', 'E19..., 'E10', ...]) == ([('T1', 'E19..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-6]` (failed): AssertionError: assert ([('T0', 'E16..., 'E11', ...]) == ([('T0', 'E20..., 'E11', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-7]` (failed): AssertionError: assert ([('T6', 'E19...', 'E8', ...]) == ([('T6', 'E19...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-8]` (failed): AssertionError: assert ([('T0', 'E3'......], ['E10']) == ([('T0', 'E3'......], ['E10'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-9]` (failed): AssertionError: assert ([('T1', 'E1'...', 'E7', ...]) == ([('T1', 'E1'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-11]` (failed): AssertionError: assert ([('T0', 'E27..., 'E18', ...]) == ([('T0', 'E27..., 'E18', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-13]` (failed): AssertionError: assert ([('T0', 'E4'...'E10', 'E15']) == ([('T0', 'E4'...'E10', 'E15'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-14]` (failed): AssertionError: assert ([('T3', 'E0'... ...], ['E5']) == ([('T3', 'E0'... ...], ['E5'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-16]` (failed): AssertionError: assert ([('T1', 'E6'...', 'E7', ...]) == ([('T1', 'E15...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-17]` (failed): AssertionError: assert ([('T0', 'E9'..., 'E20', ...]) == ([('T0', 'E9'..., 'E16', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-18]` (failed): AssertionError: assert ([('T1', 'E7'... 'E8', 'E10']) == ([('T1', 'E7'... 'E8', 'E10'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-21]` (failed): AssertionError: assert ([('T3', 'E1'...', 'E8', ...]) == ([('T3', 'E1'...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-22]` (failed): AssertionError: assert ([('T5', 'E3'..., 'E5', 'E6']) == ([('T5', 'E3'..., 'E5', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-23]` (failed): AssertionError: assert ([('T0', 'E4'...', 'E9', ...]) == ([('T0', 'E4'...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-24]` (failed): AssertionError: assert ([('T1', 'E4'..., 'E11', ...]) == ([('T1', 'E4'..., 'E11', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-25]` (failed): AssertionError: assert ([('T0', 'E0'...', 'E6', ...]) == ([('T0', 'E0'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-26]` (failed): AssertionError: assert ([('T0', 'E4'..., 'E7', 'E8']) == ([('T0', 'E4'..., 'E1', 'E7'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-27]` (failed): AssertionError: assert ([('T0', 'E15...', 'E6', ...]) == ([('T0', 'E15...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-28]` (failed): AssertionError: assert ([('T0', 'E2'..., 'E3', 'E4']) == ([('T0', 'E2'..., 'E3', 'E4'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-29]` (failed): AssertionError: assert ([('T0', 'E27..., 'E11', ...]) == ([('T0', 'E27...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-30]` (failed): AssertionError: assert ([('T0', 'E11..., 'E12', ...]) == ([('T0', 'E7'..., 'E12', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-32]` (failed): AssertionError: assert ([('T2', 'E1'...T6', ...], []) == ([('T2', 'E1'...T6', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-34]` (failed): AssertionError: assert ([('T0', 'E25...', 'E8', ...]) == ([('T0', 'E25...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-35]` (failed): AssertionError: assert ([('T0', 'E4'..., 'E16', ...]) == ([('T0', 'E4'..., 'E16', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-36]` (failed): AssertionError: assert ([('T3', 'E10...', 'E7', ...]) == ([('T3', 'E10...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-37]` (failed): AssertionError: assert ([('T0', 'E13..., 'E14', ...]) == ([('T0', 'E13...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-38]` (failed): AssertionError: assert ([('T1', 'E19..., 'E10', ...]) == ([('T1', 'E19..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-39]` (failed): AssertionError: assert ([('T0', 'E4'... 'E8', 'E12']) == ([('T0', 'E4'... 'E8', 'E12'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-40]` (failed): AssertionError: assert ([('T0', 'E2'...', 'E7', ...]) == ([('T0', 'E2'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-41]` (failed): AssertionError: assert ([('T1', 'E20..., 'E11', ...]) == ([('T1', 'E20..., 'E11', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-42]` (failed): AssertionError: assert ([('T4', 'E2'... ...], ['E3']) == ([('T4', 'E2'... ...], ['E3'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-44]` (failed): AssertionError: assert ([('T1', 'E12...', 'E9', ...]) == ([('T1', 'E12...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-47]` (failed): AssertionError: assert ([('T1', 'E16..., 'E13', ...]) == ([('T1', 'E16..., 'E13', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-48]` (failed): AssertionError: assert ([('T0', 'E9'...', 'E6', ...]) == ([('T0', 'E9'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-49]` (failed): AssertionError: assert ([('T4', 'E0'... ['E1', 'E2']) == ([('T4', 'E0'... ['E1', 'E2'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-51]` (failed): AssertionError: assert ([('T1', 'E13... 'E5', 'E14']) == ([('T1', 'E13... 'E5', 'E14'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-52]` (failed): AssertionError: assert ([('T1', 'E7'..., 'E11', ...]) == ([('T1', 'E7'..., 'E11', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-54]` (failed): AssertionError: assert ([('T3', 'E2'... ['E1', 'E6']) == ([('T3', 'E2'... ['E1', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-55]` (failed): AssertionError: assert ([('T0', 'E0'..., 'E3', 'E4']) == ([('T0', 'E0'..., 'E3', 'E4'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-56]` (failed): AssertionError: assert ([('T0', 'E4'..., 'E14', ...]) == ([('T0', 'E4'..., 'E14', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-57]` (failed): AssertionError: assert ([('T2', 'E0'...T6', ...], []) == ([('T2', 'E0'...T6', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-58]` (failed): AssertionError: assert ([('T0', 'E5'...', 'E6', ...]) == ([('T0', 'E5'...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-59]` (failed): AssertionError: assert ([('T3', 'E4'... 'E5', 'E13']) == ([('T3', 'E4'... 'E5', 'E13'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-60]` (failed): AssertionError: assert ([('T0', 'E10...'E16', 'E17']) == ([('T0', 'E10... 'E9', 'E16'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-62]` (failed): AssertionError: assert ([('T1', 'E19..., 'E11', ...]) == ([('T1', 'E19..., 'E11', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-63]` (failed): AssertionError: assert ([('T0', 'E9'...', 'E6', ...]) == ([('T0', 'E9'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-64]` (failed): AssertionError: assert ([('T0', 'E6'...', 'E9', ...]) == ([('T0', 'E13...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-65]` (failed): AssertionError: assert ([('T0', 'E6'..., 'E20', ...]) == ([('T0', 'E6'..., 'E20', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-66]` (failed): AssertionError: assert ([('T1', 'E2'... ['E0', 'E3']) == ([('T1', 'E2'... ['E0', 'E3'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-68]` (failed): AssertionError: assert ([('T0', 'E7'..., 'E11', ...]) == ([('T0', 'E28..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-70]` (failed): AssertionError: assert ([('T2', 'E5'..., 'E4', 'E6']) == ([('T2', 'E5'..., 'E4', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-72]` (failed): AssertionError: assert ([('T10', 'E0..., 'E2', 'E3']) == ([('T10', 'E0..., 'E2', 'E3'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-73]` (failed): AssertionError: assert ([('T1', 'E4'...', 'E6', ...]) == ([('T1', 'E4'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-74]` (failed): AssertionError: assert ([('T0', 'E4'...', 'E8', ...]) == ([('T0', 'E26...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-75]` (failed): AssertionError: assert ([('T1', 'E24..., 'E11', ...]) == ([('T1', 'E24...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-76]` (failed): AssertionError: assert ([('T0', 'E20..., 'E11', ...]) == ([('T0', 'E20..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-77]` (failed): AssertionError: assert ([('T4', 'E0'..., 'E14', ...]) == ([('T4', 'E0'..., 'E14', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-78]` (failed): AssertionError: assert ([('T2', 'E3'...', 'E9', ...]) == ([('T2', 'E3'...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-79]` (failed): AssertionError: assert ([('T0', 'E2'...', 'E6', ...]) == ([('T0', 'E2'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-80]` (failed): AssertionError: assert ([('T1', 'E4'...'E12', 'E14']) == ([('T1', 'E4'...'E12', 'E14'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-81]` (failed): AssertionError: assert ([('T0', 'E26...', 'E6', ...]) == ([('T0', 'E26...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-82]` (failed): AssertionError: assert ([('T3', 'E4'..., 'E7', 'E8']) == ([('T3', 'E4'..., 'E7', 'E8'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-83]` (failed): AssertionError: assert ([('T0', 'E24..., 'E13', ...]) == ([('T0', 'E24..., 'E12', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-88]` (failed): AssertionError: assert ([('T3', 'E9'...'E20', 'E24']) == ([('T3', 'E9'...'E20', 'E24'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-90]` (failed): AssertionError: assert ([('T0', 'E1'...', 'E7', ...]) == ([('T0', 'E5'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-92]` (failed): AssertionError: assert ([('T0', 'E6'...', 'E9', ...]) == ([('T0', 'E6'...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-93]` (failed): AssertionError: assert ([('T1', 'E9'..., 'E15', ...]) == ([('T1', 'E9'..., 'E15', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-94]` (failed): AssertionError: assert ([('T0', 'E7'..., 'E11', ...]) == ([('T0', 'E7'..., 'E13', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-95]` (failed): AssertionError: assert ([('T2', 'E31..., 'E14', ...]) == ([('T2', 'E31..., 'E14', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-96]` (failed): AssertionError: assert ([('T1', 'E7'...', 'E8', ...]) == ([('T1', 'E14...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-98]` (failed): AssertionError: assert ([('T2', 'E0'...', 'E7', ...]) == ([('T2', 'E17...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-99]` (failed): AssertionError: assert ([('T0', 'E9'...', 'E8', ...]) == ([('T0', 'E21...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-101]` (failed): AssertionError: assert ([('T0', 'E12...', 'E6', ...]) == ([('T0', 'E12...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-105]` (failed): AssertionError: assert ([('T1', 'E7'..., 'E13', ...]) == ([('T1', 'E7'..., 'E15', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-107]` (failed): AssertionError: assert ([('T1', 'E2'..., 'E1', 'E9']) == ([('T1', 'E2'... 'E9', 'E11'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-108]` (failed): AssertionError: assert ([('T5', 'E5'... ['E1', 'E3']) == ([('T5', 'E5'... ['E1', 'E3'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-110]` (failed): AssertionError: assert ([('T0', 'E19...', 'E8', ...]) == ([('T0', 'E19...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-111]` (failed): AssertionError: assert ([('T1', 'E9'......], ['E12']) == ([('T1', 'E9'......], ['E12'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-115]` (failed): AssertionError: assert ([('T0', 'E2'...'E10', 'E17']) == ([('T0', 'E2'...'E10', 'E17'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-116]` (failed): AssertionError: assert ([('T0', 'E24..., 'E15', ...]) == ([('T0', 'E24..., 'E15', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-117]` (failed): AssertionError: assert ([('T1', 'E5'... 'E9', 'E10']) == ([('T1', 'E5'..., 'E3', 'E9'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-118]` (failed): AssertionError: assert ([('T0', 'E1'..., 'E2', 'E9']) == ([('T0', 'E1'..., 'E2', 'E9'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-119]` (failed): AssertionError: assert ([('T1', 'E4'...', 'E9', ...]) == ([('T1', 'E4'...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-120]` (failed): AssertionError: assert ([('T0', 'E3'...', 'E6', ...]) == ([('T0', 'E3'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-121]` (failed): AssertionError: assert ([('T0', 'E1'..., 'E3', 'E4']) == ([('T0', 'E1'..., 'E3', 'E4'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-122]` (failed): AssertionError: assert ([('T1', 'E14..., 'E17', ...]) == ([('T1', 'E14..., 'E17', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-124]` (failed): AssertionError: assert ([('T1', 'E6'... 'E8', 'E16']) == ([('T1', 'E6'... 'E8', 'E16'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-125]` (failed): AssertionError: assert ([('T1', 'E2'... 'E5', 'E14']) == ([('T1', 'E2'... 'E5', 'E14'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-127]` (failed): AssertionError: assert ([('T6', 'E1'...T5', ...], []) == ([('T6', 'E1'...T5', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-128]` (failed): AssertionError: assert ([('T3', 'E13...'E12', 'E14']) == ([('T3', 'E13...'E11', 'E12'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-129]` (failed): AssertionError: assert ([('T0', 'E4'...', 'E6', ...]) == ([('T0', 'E4'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-130]` (failed): AssertionError: assert ([('T2', 'E23...', 'E7', ...]) == ([('T2', 'E23...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-131]` (failed): AssertionError: assert ([('T0', 'E10...', 'E5', ...]) == ([('T0', 'E10...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-132]` (failed): AssertionError: assert ([('T0', 'E8'..., 'E13', ...]) == ([('T0', 'E8'..., 'E12', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-134]` (failed): AssertionError: assert ([('T0', 'E12...', 'E8', ...]) == ([('T0', 'E12...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-136]` (failed): AssertionError: assert ([('T0', 'E0'..., 'E16', ...]) == ([('T0', 'E15..., 'E16', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-138]` (failed): AssertionError: assert ([('T3', 'E2'...'E10', 'E11']) == ([('T3', 'E2'...'E10', 'E11'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-141]` (failed): AssertionError: assert ([('T1', 'E7'...', 'E6', ...]) == ([('T1', 'E12...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-142]` (failed): AssertionError: assert ([('T1', 'E14..., 'E13', ...]) == ([('T1', 'E14...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-143]` (failed): AssertionError: assert ([('T1', 'E0'... ...], ['E7']) == ([('T1', 'E0'... ...], ['E7'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-144]` (failed): AssertionError: assert ([('T0', 'E0'...', 'E8', ...]) == ([('T0', 'E0'...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-145]` (failed): AssertionError: assert ([('T1', 'E19...', 'E9', ...]) == ([('T1', 'E19...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-147]` (failed): AssertionError: assert ([('T0', 'E26..., 'E10', ...]) == ([('T0', 'E26..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[1-148]` (failed): AssertionError: assert ([('T0', 'E0'..., 'E20', ...]) == ([('T0', 'E0'..., 'E17', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-0]` (failed): AssertionError: assert ([('T0', 'E17...'E15', 'E23']) == ([('T0', 'E17...'E14', 'E18'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-1]` (failed): AssertionError: assert ([('T0', 'E6'...T8', ...], []) == ([('T0', 'E6'...T8', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-2]` (failed): AssertionError: assert ([('T4', 'E0'...T7', ...], []) == ([('T4', 'E0'...T7', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-3]` (failed): AssertionError: assert ([('T0', 'E5'...', 'E6', ...]) == ([('T0', 'E5'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-5]` (failed): AssertionError: assert ([('T0', 'E27..., 'E12', ...]) == ([('T0', 'E27..., 'E12', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-6]` (failed): AssertionError: assert ([('T0', 'E16..., 'E12', ...]) == ([('T0', 'E20..., 'E12', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-7]` (failed): AssertionError: assert ([('T3', 'E12..., 'E10', ...]) == ([('T3', 'E15..., 'E11', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-8]` (failed): AssertionError: assert ([('T0', 'E3'...13', ...], []) == ([('T0', 'E3'...13', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-9]` (failed): AssertionError: assert ([('T0', 'E1'..., 'E12', ...]) == ([('T0', 'E1'..., 'E12', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-10]` (failed): AssertionError: assert ([('T0', 'E34...', 'E6', ...]) == ([('T0', 'E34...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-11]` (failed): AssertionError: assert ([('T0', 'E27...'E22', 'E25']) == ([('T0', 'E27...'E17', 'E22'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-13]` (failed): AssertionError: assert ([('T0', 'E4'......], ['E15']) == ([('T0', 'E4'... ...], ['E0'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-14]` (failed): AssertionError: assert ([('T3', 'E0'...T6', ...], []) == ([('T3', 'E0'...T6', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-15]` (failed): AssertionError: assert ([('T0', 'E1'...', 'E7', ...]) == ([('T0', 'E1'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-16]` (failed): AssertionError: assert ([('T1', 'E6'...', 'E8', ...]) == ([('T1', 'E15...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-17]` (failed): AssertionError: assert ([('T0', 'E9'..., 'E28', ...]) == ([('T0', 'E17..., 'E28', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-18]` (failed): AssertionError: assert ([('T0', 'E1'... ...], ['E5']) == ([('T0', 'E1'... ...], ['E5'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-20]` (failed): AssertionError: assert ([('T0', 'E6'...14', ...], []) == ([('T0', 'E6'...14', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-21]` (failed): AssertionError: assert ([('T0', 'E4'..., 'E8', 'E9']) == ([('T0', 'E4'..., 'E8', 'E9'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-22]` (failed): AssertionError: assert ([('T0', 'E3'... ['E5', 'E6']) == ([('T0', 'E3'... ['E1', 'E5'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-23]` (failed): AssertionError: assert ([('T0', 'E4'...'E15', 'E17']) == ([('T0', 'E4'...'E15', 'E17'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-24]` (failed): AssertionError: assert ([('T0', 'E5'..., 'E19', ...]) == ([('T0', 'E5'..., 'E19', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-25]` (failed): AssertionError: assert ([('T0', 'E0'...', 'E6', ...]) == ([('T0', 'E0'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-26]` (failed): AssertionError: assert ([('T0', 'E4'...15', ...], []) == ([('T0', 'E4'...15', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-27]` (failed): AssertionError: assert ([('T0', 'E15...', 'E6', ...]) == ([('T0', 'E25...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-29]` (failed): AssertionError: assert ([('T0', 'E27..., 'E12', ...]) == ([('T0', 'E27...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-30]` (failed): AssertionError: assert ([('T0', 'E11..., 'E16', ...]) == ([('T0', 'E7'..., 'E15', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-32]` (failed): AssertionError: assert ([('T2', 'E1'...T9', ...], []) == ([('T2', 'E1'...T9', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-33]` (failed): AssertionError: assert ([('T0', 'E29...', 'E6', ...]) == ([('T0', 'E21...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-34]` (failed): AssertionError: assert ([('T0', 'E25..., 'E13', ...]) == ([('T0', 'E12...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-35]` (failed): AssertionError: assert ([('T0', 'E4'..., 'E22', ...]) == ([('T0', 'E4'..., 'E22', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-36]` (failed): AssertionError: assert ([('T3', 'E10..., 'E15', ...]) == ([('T3', 'E10..., 'E15', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-37]` (failed): AssertionError: assert ([('T0', 'E13..., 'E16', ...]) == ([('T0', 'E13..., 'E19', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-38]` (failed): AssertionError: assert ([('T1', 'E19..., 'E13', ...]) == ([('T1', 'E19..., 'E13', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-39]` (failed): AssertionError: assert ([('T0', 'E4'...['E7', 'E12']) == ([('T0', 'E4'...['E7', 'E12'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-40]` (failed): AssertionError: assert ([('T0', 'E2'...', 'E8', ...]) == ([('T0', 'E2'...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-41]` (failed): AssertionError: assert ([('T0', 'E4'... 'E9', 'E13']) == ([('T0', 'E4'...'E13', 'E15'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-44]` (failed): AssertionError: assert ([('T0', 'E22..., 'E10', ...]) == ([('T0', 'E22..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-47]` (failed): AssertionError: assert ([('T0', 'E10... 'E2', 'E14']) == ([('T0', 'E10... 'E2', 'E14'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-48]` (failed): AssertionError: assert ([('T0', 'E9'...', 'E6', ...]) == ([('T0', 'E9'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-51]` (failed): AssertionError: assert ([('T0', 'E13...17', ...], []) == ([('T0', 'E13...17', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-52]` (failed): AssertionError: assert ([('T0', 'E7'...'E12', 'E16']) == ([('T0', 'E7'...'E12', 'E16'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-53]` (failed): AssertionError: assert ([('T0', 'E32...', 'E5', ...]) == ([('T0', 'E32...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-54]` (failed): AssertionError: assert ([('T0', 'E1'...T9', ...], []) == ([('T0', 'E1'...10', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-55]` (failed): AssertionError: assert ([('T0', 'E0'..., 'E3', 'E4']) == ([('T0', 'E0'..., 'E3', 'E4'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-56]` (failed): AssertionError: assert ([('T0', 'E4'..., 'E21', ...]) == ([('T0', 'E4'..., 'E18', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-57]` (failed): AssertionError: assert ([('T2', 'E0'...T6', ...], []) == ([('T2', 'E0'...T6', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-58]` (failed): AssertionError: assert ([('T0', 'E5'...', 'E6', ...]) == ([('T0', 'E5'...', 'E9', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-59]` (failed): AssertionError: assert ([('T0', 'E12... ...], ['E2']) == ([('T0', 'E12... ...], ['E2'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-60]` (failed): AssertionError: assert ([('T0', 'E10...23', ...], []) == ([('T0', 'E10...23', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-62]` (failed): AssertionError: assert ([('T0', 'E22..., 'E18', ...]) == ([('T0', 'E22..., 'E18', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-63]` (failed): AssertionError: assert ([('T0', 'E9'..., 'E10', ...]) == ([('T0', 'E9'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-64]` (failed): AssertionError: assert ([('T0', 'E6'..., 'E21', ...]) == ([('T0', 'E13..., 'E20', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-65]` (failed): AssertionError: assert ([('T0', 'E6'..., 'E23', ...]) == ([('T0', 'E6'..., 'E21', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-66]` (failed): AssertionError: assert ([('T1', 'E2'...8', 'T9'], []) == ([('T1', 'E2'...8', 'T9'], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-68]` (failed): AssertionError: assert ([('T0', 'E7'..., 'E21', ...]) == ([('T0', 'E28..., 'E22', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-70]` (failed): AssertionError: assert ([('T2', 'E5'..., 'E4', 'E6']) == ([('T2', 'E5'..., 'E4', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-72]` (failed): AssertionError: assert ([('T2', 'E2'...T6', ...], []) == ([('T2', 'E2'...T6', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-73]` (failed): AssertionError: assert ([('T0', 'E0'...', 'E8', ...]) == ([('T0', 'E0'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-74]` (failed): AssertionError: assert ([('T0', 'E4'...', 'E9', ...]) == ([('T0', 'E26...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-75]` (failed): AssertionError: assert ([('T0', 'E8'..., 'E13', ...]) == ([('T0', 'E8'..., 'E13', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-76]` (failed): AssertionError: assert ([('T0', 'E20..., 'E14', ...]) == ([('T0', 'E12..., 'E15', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-77]` (failed): AssertionError: assert ([('T0', 'E12... ['E1', 'E6']) == ([('T0', 'E12... ['E1', 'E6'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-78]` (failed): AssertionError: assert ([('T2', 'E3'...['E2', 'E10']) == ([('T2', 'E3'...['E2', 'E10'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-79]` (failed): AssertionError: assert ([('T0', 'E2'...', 'E6', ...]) == ([('T0', 'E2'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-80]` (failed): AssertionError: assert ([('T1', 'E4'...['E2', 'E14']) == ([('T1', 'E4'...['E2', 'E14'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-81]` (failed): AssertionError: assert ([('T0', 'E26...', 'E7', ...]) == ([('T0', 'E26...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-82]` (failed): AssertionError: assert ([('T0', 'E7'... ...], ['E8']) == ([('T0', 'E7'... ...], ['E8'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-83]` (failed): AssertionError: assert ([('T0', 'E24..., 'E18', ...]) == ([('T0', 'E24..., 'E19', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-85]` (failed): AssertionError: assert ([('T0', 'E3'... 'E8', 'E11']) == ([('T0', 'E3'... 'E8', 'E11'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-86]` (failed): AssertionError: assert ([('T13', 'E0...T5', ...], []) == ([('T13', 'E0...T5', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-87]` (failed): AssertionError: assert ([('T1', 'E3'..., 'E5', 'E7']) == ([('T1', 'E3'..., 'E5', 'E7'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-88]` (failed): AssertionError: assert ([('T1', 'E23...'E17', 'E20']) == ([('T1', 'E23...'E17', 'E20'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-89]` (failed): AssertionError: assert ([('T2', 'E3'... ['E1', 'E4']) == ([('T2', 'E3'... ['E1', 'E4'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-90]` (failed): AssertionError: assert ([('T0', 'E1'...', 'E7', ...]) == ([('T0', 'E5'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-91]` (failed): AssertionError: assert ([('T0', 'E1'..., 'E3', 'E4']) == ([('T0', 'E1'..., 'E3', 'E4'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-92]` (failed): AssertionError: assert ([('T0', 'E6'..., 'E22', ...]) == ([('T0', 'E6'..., 'E22', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-93]` (failed): AssertionError: assert ([('T0', 'E13..., 'E18', ...]) == ([('T0', 'E13..., 'E17', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-94]` (failed): AssertionError: assert ([('T0', 'E7'..., 'E13', ...]) == ([('T0', 'E7'..., 'E12', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-95]` (failed): AssertionError: assert ([('T0', 'E9'..., 'E16', ...]) == ([('T0', 'E9'..., 'E16', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-96]` (failed): AssertionError: assert ([('T1', 'E7'...', 'E8', ...]) == ([('T1', 'E14...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-98]` (failed): AssertionError: assert ([('T0', 'E9'...', 'E7', ...]) == ([('T0', 'E9'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-99]` (failed): AssertionError: assert ([('T0', 'E9'..., 'E10', ...]) == ([('T0', 'E21...', 'E8', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-100]` (failed): AssertionError: assert ([('T1', 'E5'..., 'E4', 'E8']) == ([('T1', 'E5'..., 'E4', 'E8'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-101]` (failed): AssertionError: assert ([('T0', 'E12...', 'E6', ...]) == ([('T0', 'E12...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-102]` (failed): AssertionError: assert ([('T0', 'E7'... ['E3', 'E4']) == ([('T0', 'E7'...T11'], ['E3'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-103]` (failed): AssertionError: assert ([('T0', 'E8'...', 'E5', ...]) == ([('T0', 'E2'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-105]` (failed): AssertionError: assert ([('T0', 'E33..., 'E19', ...]) == ([('T0', 'E33..., 'E26', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-107]` (failed): AssertionError: assert ([('T0', 'E13... ...], ['E9']) == ([('T0', 'E13... ['E0', 'E9'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-109]` (failed): AssertionError: assert ([('T0', 'E8'...'E11', 'E13']) == ([('T0', 'E13... 'E8', 'E11'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-110]` (failed): AssertionError: assert ([('T0', 'E19..., 'E10', ...]) == ([('T0', 'E19..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-111]` (failed): AssertionError: assert ([('T0', 'E6'...17', ...], []) == ([('T0', 'E6'...17', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-112]` (failed): AssertionError: assert ([('T0', 'E1'..., 'E10', ...]) == ([('T0', 'E1'...', 'E7', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-115]` (failed): AssertionError: assert ([('T0', 'E2'...'E10', 'E17']) == ([('T0', 'E2'...'E10', 'E17'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-116]` (failed): AssertionError: assert ([('T0', 'E24..., 'E25', ...]) == ([('T0', 'E24..., 'E25', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-117]` (failed): AssertionError: assert ([('T0', 'E1'......], ['E10']) == ([('T0', 'E1'...17', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-118]` (failed): AssertionError: assert ([('T0', 'E1'...11', ...], []) == ([('T0', 'E1'...11', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-119]` (failed): AssertionError: assert ([('T0', 'E8'..., 'E11', ...]) == ([('T0', 'E8'..., 'E11', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-120]` (failed): AssertionError: assert ([('T0', 'E3'...', 'E8', ...]) == ([('T0', 'E28...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-121]` (failed): AssertionError: assert ([('T0', 'E1'...T9', ...], []) == ([('T0', 'E1'...T9', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-122]` (failed): AssertionError: assert ([('T0', 'E23..., 'E21', ...]) == ([('T0', 'E23..., 'E21', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-124]` (failed): AssertionError: assert ([('T1', 'E6'... ['E4', 'E8']) == ([('T1', 'E6'... ['E4', 'E8'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-125]` (failed): AssertionError: assert ([('T1', 'E2'...14', ...], []) == ([('T1', 'E2'...14', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-127]` (failed): AssertionError: assert ([('T1', 'E1'...T6', ...], []) == ([('T1', 'E1'...T6', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-128]` (failed): AssertionError: assert ([('T0', 'E11... 'E8', 'E12']) == ([('T0', 'E14... 'E8', 'E12'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-129]` (failed): AssertionError: assert ([('T0', 'E4'...', 'E6', ...]) == ([('T0', 'E4'...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-130]` (failed): AssertionError: assert ([('T1', 'E18..., 'E10', ...]) == ([('T1', 'E20...', 'E6', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-131]` (failed): AssertionError: assert ([('T0', 'E10...', 'E5', ...]) == ([('T0', 'E10...', 'E5', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-132]` (failed): AssertionError: assert ([('T0', 'E8'...'E13', 'E15']) == ([('T0', 'E8'...'E13', 'E15'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-134]` (failed): AssertionError: assert ([('T0', 'E12..., 'E13', ...]) == ([('T0', 'E8'..., 'E13', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-136]` (failed): AssertionError: assert ([('T0', 'E0'..., 'E25', ...]) == ([('T0', 'E15..., 'E26', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-138]` (failed): AssertionError: assert ([('T1', 'E10......], ['E11']) == ([('T1', 'E10......], ['E11'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-140]` (failed): AssertionError: assert ([('T1', 'E3'..., 'E2', 'E4']) == ([('T1', 'E3'..., 'E2', 'E4'])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-141]` (failed): AssertionError: assert ([('T0', 'E14..., 'E15', ...]) == ([('T0', 'E14..., 'E20', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-142]` (failed): AssertionError: assert ([('T0', 'E0'..., 'E24', ...]) == ([('T0', 'E0'..., 'E16', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-143]` (failed): AssertionError: assert ([('T1', 'E0'...11', ...], []) == ([('T1', 'E0'...11', ...], [])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-144]` (failed): AssertionError: assert ([('T0', 'E0'..., 'E10', ...]) == ([('T0', 'E0'..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-145]` (failed): AssertionError: assert ([('T1', 'E19..., 'E15', ...]) == ([('T1', 'E2'..., 'E16', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-147]` (failed): AssertionError: assert ([('T0', 'E26..., 'E12', ...]) == ([('T0', 'E26..., 'E10', ...])
- `hidden.test_equivalence::test_dense_random_inputs_match_oracle[3-148]` (failed): AssertionError: assert ([('T0', 'E0'... ...], ['E4']) == ([('T0', 'E0'... ['E3', 'E4'])
- `hidden.test_equivalence::test_realistic_workload_matches_oracle[1]` (failed): AssertionError: assert ([('T0000001'...000009', ...]) == ([('T0000001'...000009', ...])
- `hidden.test_equivalence::test_realistic_workload_matches_oracle[2]` (failed): AssertionError: assert ([('T0000000'...000013', ...]) == ([('T0000000'...000013', ...])
- `hidden.test_equivalence::test_realistic_workload_matches_oracle[3]` (failed): AssertionError: assert ([('T0000000'...000009', ...]) == ([('T0000000'...000009', ...])
- `visible.test_reconcile::test_reference_hit_beats_date_proximity_case_insensitively` (failed): AssertionError: assert [('T1', 'E1')] == [('T1', 'E2')]

## t03_pricing_legacy / baseline

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`

Failing tests:

- `hidden.test_new_rules_edges::test_norway_has_no_reduced_book_rate_and_gift_cards_stay_untaxed` (failed): ValueError: unsupported country: NO
- `hidden.test_new_rules_edges::test_norway_shipping_matches_other_international_destinations` (failed): ValueError: unsupported country: NO
- `hidden.test_new_rules_edges::test_norway_volume_and_tier_discounts_reduce_the_tax_base` (failed): ValueError: unsupported country: NO
- `hidden.test_new_rules_edges::test_save15_does_not_discount_gift_cards` (failed): assert 0 == 1500
- `hidden.test_new_rules_edges::test_every_supported_country_prices_a_basic_order[NO]` (failed): ValueError: unsupported country: NO
- `visible.test_new_rules::test_norway_charges_25_percent_vat_on_goods_and_shipping` (failed): ValueError: unsupported country: NO
- `visible.test_new_rules::test_norway_is_not_eligible_for_eu_reverse_charge` (failed): ValueError: unsupported country: NO
- `visible.test_new_rules::test_save15_takes_15_percent_capped_at_7500` (failed): assert 0 == 2400
- `visible.test_new_rules::test_save15_applies_after_tier_discount_and_not_for_platinum` (failed): AssertionError: assert {'coupon': 0,..., 'volume': 0} == {'coupon': 22..., 'volume': 0}
- `visible.test_structure::test_no_function_is_too_complex_or_too_long` (failed): AssertionError: limits are complexity<=10, lines<=40: ['pricing.py:price_order (complexity 42, 123 lines)']

## t03_pricing_legacy / reference

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `d7287e3889cf9a0c2f69985a2560da92fbce29062087ced9be51fe13b5a2ef41`

## t03_pricing_legacy / candidate:candidates/patch_in_place.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `561369f8b04e2dc65089f9891659ef9e3899405a461e09361648bd08709bef8e`

Failing tests:

- `visible.test_structure::test_no_function_is_too_complex_or_too_long` (failed): AssertionError: limits are complexity<=10, lines<=40: ['pricing.py:price_order (complexity 45, 128 lines)']

## t03_pricing_legacy / candidate:candidates/refactor_changes_rounding.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `2c5b5627802e991ac79a207406ad1c05b8b9feb0d1f5a4e37c3522f39d73e6cb`

Failing tests:

- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_002]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_003]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_007]` (failed): AssertionError: assert {'applied': [...g': 1699, ...} == {'applied': [...g': 1699, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_037]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_045]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_092]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_097]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_126]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_149]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_185]` (failed): AssertionError: assert {'applied': [...g': 3399, ...} == {'applied': [...g': 3399, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_186]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_196]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_200]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_208]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_209]` (failed): AssertionError: assert {'applied': [...g': 2999, ...} == {'applied': [...g': 2999, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_215]` (failed): AssertionError: assert {'applied': [...g': 5499, ...} == {'applied': [...g': 5499, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_248]` (failed): AssertionError: assert {'applied': [...g': 3999, ...} == {'applied': [...g': 3999, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_279]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_289]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_294]` (failed): AssertionError: assert {'applied': [...g': 4299, ...} == {'applied': [...g': 4299, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_303]` (failed): AssertionError: assert {'applied': [...g': 2199, ...} == {'applied': [...g': 2199, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_313]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_324]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_359]` (failed): AssertionError: assert {'applied': [...g': 2199, ...} == {'applied': [...g': 2199, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_364]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_403]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_411]` (failed): AssertionError: assert {'applied': [...g': 2599, ...} == {'applied': [...g': 2599, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_419]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_452]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_454]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_462]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_487]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_510]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_519]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_524]` (failed): AssertionError: assert {'applied': [...g': 5599, ...} == {'applied': [...g': 5599, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_535]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_542]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `hidden.test_golden_hidden::test_matches_recorded_behavior[random_563]` (failed): AssertionError: assert {'applied': [...ng': 800, ...} == {'applied': [...ng': 800, ...}
- `visible.test_golden::test_matches_recorded_behavior[half_even_rounding_quirk]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}
- `visible.test_golden::test_matches_recorded_behavior[mixed_lines_discount_allocation]` (failed): AssertionError: assert {'applied': [...ping': 0, ...} == {'applied': [...ping': 0, ...}

## t04_webhook_pr / baseline

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Defects resolved: 0/9 (unresolved: 01, 02, 03, 04, 05, 06, 07, 08, 09)

Failing tests:

- `hidden.test_delivery_defects::test_defect_06_backoff_starts_at_base_delay_doubles_and_is_capped` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_no_sleep_after_the_final_attempt_or_after_success` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_defect_07_exhausted_retries_raise_with_details` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_defect_07_last_network_error_is_preserved` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_defect_07_permanent_failure_raises_after_one_attempt` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_defect_08_programming_errors_are_not_swallowed_or_retried` (failed): Failed: DID NOT RAISE <class 'ValueError'>
- `hidden.test_delivery_defects::test_defect_09_every_delivery_gets_its_own_webhook_id` (failed): AssertionError: assert 1 == 2
- `hidden.test_delivery_defects::test_defect_09_callers_headers_are_not_mutated_and_are_forwarded` (failed): AssertionError: assert {'Content-Typ...559c4ad', ...} == {'X-Tenant': ...': 'fixed-id'}
- `hidden.test_signing_defects::test_defect_01_signature_is_compared_in_constant_time` (failed): AssertionError: verify() never used a constant-time comparison
- `hidden.test_signing_defects::test_defect_02_stale_and_future_timestamps_are_rejected` (failed): assert not True
- `hidden.test_signing_defects::test_defect_03_timestamp_is_covered_by_the_signature` (failed): assert 'v1=5910e62016ef5034272c926c27071992a465c2335cecf41851bda071577f4f6d' != 'v1=5910e62016ef5034272c926c27071992a465c2335cecf41851bda071577f4f6d'
- `visible.test_delivery::test_defect_04_permanent_failures_are_not_retried` (failed): AssertionError: status 400 was retried
- `visible.test_delivery::test_defect_05_max_attempts_is_the_total_number_of_tries` (failed): assert 4 == 3

## t04_webhook_pr / reference

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Defects resolved: 9/9
- Patch sha256: `7ef1a70b4d28a12c19f9cd2c6ec7689c86fd1f2feef6fa30f58faf2828ece84f`

## t04_webhook_pr / candidate:candidates/naive_quick_fixes.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Defects resolved: 2/9 (unresolved: 02, 03, 04, 06, 07, 08, 09)
- Patch sha256: `882bcb098fd7cb06a8e8228047fff11c00e995160889bd9bb58742283eee8d0d`

Failing tests:

- `hidden.test_delivery_defects::test_defect_06_backoff_starts_at_base_delay_doubles_and_is_capped` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_no_sleep_after_the_final_attempt_or_after_success` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_defect_07_exhausted_retries_raise_with_details` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_defect_07_last_network_error_is_preserved` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_defect_07_permanent_failure_raises_after_one_attempt` (failed): Failed: DID NOT RAISE <class 'hooks.delivery.DeliveryFailed'>
- `hidden.test_delivery_defects::test_defect_08_programming_errors_are_not_swallowed_or_retried` (failed): Failed: DID NOT RAISE <class 'ValueError'>
- `hidden.test_delivery_defects::test_defect_09_every_delivery_gets_its_own_webhook_id` (failed): AssertionError: assert 1 == 2
- `hidden.test_delivery_defects::test_defect_09_callers_headers_are_not_mutated_and_are_forwarded` (failed): AssertionError: assert {'Content-Typ...559c4ad', ...} == {'X-Tenant': ...': 'fixed-id'}
- `hidden.test_signing_defects::test_malformed_or_non_ascii_signatures_are_rejected_without_error[v1=\xe9]` (failed): TypeError: comparing strings with non-ASCII characters is not supported
- `hidden.test_signing_defects::test_malformed_or_non_ascii_signatures_are_rejected_without_error[\u202e]` (failed): TypeError: comparing strings with non-ASCII characters is not supported
- `hidden.test_signing_defects::test_defect_02_stale_and_future_timestamps_are_rejected` (failed): assert not True
- `hidden.test_signing_defects::test_defect_03_timestamp_is_covered_by_the_signature` (failed): assert 'v1=5910e62016ef5034272c926c27071992a465c2335cecf41851bda071577f4f6d' != 'v1=5910e62016ef5034272c926c27071992a465c2335cecf41851bda071577f4f6d'
- `visible.test_delivery::test_defect_04_permanent_failures_are_not_retried` (failed): AssertionError: status 400 was retried

## t04_webhook_pr / candidate:candidates/fix_keeps_broad_except.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 64, "timeout_s": 120, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Defects resolved: 8/9 (unresolved: 08)
- Patch sha256: `22717e1aa475927ed1b3fceccd1602b9aef491e1b6b677bcd2c203eeb39cf172`

Failing tests:

- `hidden.test_delivery_defects::test_defect_08_programming_errors_are_not_swallowed_or_retried` (failed): hooks.delivery.DeliveryFailed: delivery failed after 5 attempt(s): bug in transport

## t05_orders_api / baseline

- Limits: `{"memory": "256m", "cpus": "1", "pids": 128, "timeout_s": 180, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`

Failing tests:

- `hidden.test_idempotency_edges::test_body_is_compared_canonically` (failed): AssertionError: assert (201 == 201 and 2 == 1)
- `hidden.test_idempotency_edges::test_invalid_keys_are_rejected[]` (failed): AssertionError: assert 201 == 400
- `hidden.test_idempotency_edges::test_invalid_keys_are_rejected[ ]` (failed): AssertionError: assert 201 == 400
- `hidden.test_idempotency_edges::test_invalid_keys_are_rejected[xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]` (failed): AssertionError: assert 201 == 400
- `hidden.test_idempotency_edges::test_invalid_keys_are_rejected[tab\there]` (failed): AssertionError: assert 201 == 400
- `hidden.test_idempotency_edges::test_invalid_keys_are_rejected[na\xefve]` (failed): AssertionError: assert 201 == 400
- `hidden.test_idempotency_edges::test_invalid_keys_are_rejected[new\nline]` (failed): AssertionError: assert 201 == 400
- `hidden.test_idempotency_edges::test_replay_shows_the_order_as_it_is_now` (failed): assert (2 == 1)
- `hidden.test_idempotency_edges::test_concurrent_duplicates_create_exactly_one_order` (failed): assert 16 == 1
- `hidden.test_locking_and_migration::test_post_response_carries_version_and_etag` (failed): KeyError: 'version'
- `hidden.test_locking_and_migration::test_malformed_if_match_is_a_client_error[]` (failed): AssertionError: assert 200 in (400, 428)
- `hidden.test_locking_and_migration::test_malformed_if_match_is_a_client_error[abc]` (failed): AssertionError: assert 200 in (400, 428)
- `hidden.test_locking_and_migration::test_malformed_if_match_is_a_client_error["abc"]` (failed): AssertionError: assert 200 in (400, 428)
- `hidden.test_locking_and_migration::test_malformed_if_match_is_a_client_error["1", "2"]` (failed): AssertionError: assert 200 in (400, 428)
- `hidden.test_locking_and_migration::test_malformed_if_match_is_a_client_error[-1]` (failed): AssertionError: assert 200 in (400, 428)
- `hidden.test_locking_and_migration::test_error_precedence_is_404_then_428_then_412` (failed): AssertionError: assert 200 == 428
- `hidden.test_locking_and_migration::test_rejected_updates_do_not_bump_the_version` (failed): assert None == '"1"'
- `hidden.test_locking_and_migration::test_each_successful_update_increments_the_version` (failed): KeyError: 'version'
- `hidden.test_locking_and_migration::test_concurrent_updates_with_the_same_etag_have_one_winner` (failed): AssertionError: [200, 200, 200, 200, 200, 200, ...]
- `hidden.test_locking_and_migration::test_existing_database_is_upgraded_in_place` (failed): KeyError: 'version'
- `hidden.test_pagination_edges::test_default_limit_is_20_and_last_page_has_no_cursor` (failed): assert ([1, 2, 3, 4, 5, 6, ...] == [1, 2, 3, 4, 5, 6, ...]
- `hidden.test_pagination_edges::test_exactly_full_final_page_does_not_advertise_another_page` (failed): KeyError: 'next_cursor'
- `hidden.test_pagination_edges::test_empty_listing_has_null_cursor` (failed): AssertionError: assert (200 == 200 and {'items': []} == {'items': [],...cursor': None}
- `hidden.test_pagination_edges::test_invalid_limit_is_rejected[0]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_limit_is_rejected[-1]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_limit_is_rejected[101]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_limit_is_rejected[abc]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_limit_is_rejected[]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_limit_is_rejected[1.5]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_cursor_is_rejected[garbage]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_cursor_is_rejected[!!!!]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_cursor_is_rejected[AAAA]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_cursor_is_rejected[-1]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_invalid_cursor_is_rejected[9999999999999999999999999999999999999999]` (failed): AssertionError: assert 200 == 400
- `hidden.test_pagination_edges::test_new_orders_during_paging_are_neither_duplicated_nor_lost` (failed): KeyError: 'next_cursor'
- `hidden.test_pagination_edges::test_status_filter_with_concurrent_status_changes_does_not_skip` (failed): assert [1, 2, 3, 4, 5] == [1, 2]
- `hidden.test_pagination_edges::test_status_filter_values` (failed): assert [1, 2] == [2]
- `hidden.test_pagination_edges::test_cursors_never_leak_other_customers_orders` (failed): KeyError: 'next_cursor'
- `visible.test_new_features::test_listing_is_paginated_with_opaque_cursors` (failed): assert [1, 2, 3, 4, 5] == [1, 2]
- `visible.test_new_features::test_idempotency_key_replays_the_same_order` (failed): assert 2 == 1
- `visible.test_new_features::test_reusing_a_key_with_a_different_body_is_rejected` (failed): AssertionError: assert 201 == 422
- `visible.test_new_features::test_etag_and_if_match_protect_updates` (failed): assert (None == '"1"')

## t05_orders_api / reference

- Limits: `{"memory": "256m", "cpus": "1", "pids": 128, "timeout_s": 180, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `b599c5fa66486f1553a70e23e23ff94994e8a54673f3a52a4360b1df6c72eb47`

## t05_orders_api / candidate:candidates/offset_cursor_and_check_then_insert.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 128, "timeout_s": 180, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `77197ed021c1cb29a2bedf06f3c7347054bc9ee1d08c4ff4c35e56a509e24917`

Failing tests:

- `hidden.test_idempotency_edges::test_concurrent_duplicates_create_exactly_one_order` (failed): assert 10 == 1
- `hidden.test_pagination_edges::test_status_filter_with_concurrent_status_changes_does_not_skip` (failed): assert [4, 5] == [3, 4]
- `hidden.test_pagination_edges::test_cursors_never_leak_other_customers_orders` (failed): assert [] == [4]

## t05_orders_api / candidate:candidates/no_in_place_migration.patch

- Limits: `{"memory": "256m", "cpus": "1", "pids": 128, "timeout_s": 180, "network": "none"}`
- Image: `sha256:5692ffbb1dee39d3b1f0242653e5e373bdb9667a265e63624b6b6b2f45a037b5`
- Patch sha256: `5d0d9407935f1ad71ccd412124f00cb222454928021481f8880c44e5e45aaef6`

Failing tests:

- `hidden.test_locking_and_migration::test_existing_database_is_upgraded_in_place` (failed): sqlite3.OperationalError: no such column: idempotency_key
