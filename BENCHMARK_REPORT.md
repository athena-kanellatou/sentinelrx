# SentinelRx Synthetic Benchmark Report

**Suite:** 120 synthetic FHIR medication-transition cases  
**Ground truth:** predefined by deterministic case generator  
**Purpose:** software evaluation only; not clinical validation

| Metric | SentinelRx | Naive baseline |
|---|---:|---:|
| Precision | 1.000 | 1.000 |
| Recall | 1.000 | 0.429 |
| F1 | 1.000 | 0.600 |
| Exact case accuracy | 1.000 | 0.500 |

## Interpretation

SentinelRx is exact on this generated benchmark because the benchmark case families directly test the deterministic transition rules implemented by the engine. The result demonstrates regression correctness over these synthetic scenarios; it must **not** be described as clinical accuracy or prospective validation.

The naive baseline only performs set-level admission/discharge comparison, so it cannot detect duplicate-resource or dose-change cases.
