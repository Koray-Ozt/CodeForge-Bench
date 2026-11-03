# Benchmark: t02_ledger_reconcile

Python 3.12.16 in a container limited by Docker `--cpus` (12 host CPUs visible), repeats=5, warmup=1.

| Case | Baseline median (s) | Reference median (s) | Speedup | Baseline IQR | Reference IQR | Output digest |
|---|---|---|---|---|---|---|
| 2000x2000 | 0.1314 | 0.0020 | 66.6x | 0.0135 | 0.0001 | `ce1c091394e97a16` (identical) |
| 5000x5000 | 0.8643 | 0.0058 | 148.0x | 0.0116 | 0.0006 | `51780825167910ce` (identical) |
| 10000x10000 | 3.6893 | 0.0117 | 315.9x | 0.0559 | 0.0013 | `24823736bf8deda1` (identical) |

These are wall-clock timings from a single machine inside a CPU/memory-limited container. See the README for measurement limitations.
