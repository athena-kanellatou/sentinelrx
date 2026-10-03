# SentinelRx

**Evidence-grounded medication-transition safety for synthetic FHIR R4 data**

> The AI proposes. Deterministic code verifies. The clinician decides.

SentinelRx is a research prototype for medication-transition review at hospital discharge. It analyzes synthetic FHIR R4 medication records, surfaces potential discrepancies, links every surfaced finding to source evidence, and explicitly abstains when transition context or medication identity is insufficient.

## What it demonstrates

- admission → discharge medication timeline extraction
- deterministic discrepancy detection for omissions, additions, duplications, and dose-text changes
- evidence provenance for each surfaced finding
- explicit `VERIFIED` / `ABSTAIN` safety states
- counterfactual reruns over changed synthetic evidence
- reproducible standard and robustness benchmarks
- clinician-facing Streamlit demo
- FastAPI analysis endpoint

## Architecture

```text
FHIR R4 Bundle
      ↓
Resource validation / parsing
      ↓
Medication timeline extraction
      ↓
Deterministic candidate detection
      ↓
Evidence provenance
      ↓
Safety gate
   ↙       ↘
VERIFIED   ABSTAIN
   ↓
Clinician review
```

## Demo

```bash
pip install -e ".[dev]"
streamlit run sentinelrx/ui.py
```

API:

```bash
uvicorn sentinelrx.api:app --reload
```

## Reproducible evaluation

Standard benchmark:

```bash
python scripts/run_benchmark.py
```

Robustness benchmark:

```bash
python scripts/run_robust_benchmark.py
```

Current generated-test results:

| Metric | SentinelRx | Naive baseline |
|---|---:|---:|
| Precision | 1.000 | 1.000 |
| Recall | 1.000 | 0.429 |
| F1 | 1.000 | 0.600 |
| Exact-case accuracy | 1.000 | 0.500 |

Robustness suite:

- 90 adversarial / incomplete synthetic cases
- verified-finding exact accuracy: **1.000**
- abstention-behavior accuracy: **1.000**
- crash rate: **0.000**

These results measure deterministic behavior on generated synthetic test conditions only. They are **not clinical validation** and must not be interpreted as real-world clinical effectiveness.

## Safety boundary

SentinelRx:
- uses synthetic data for development and evaluation;
- does not diagnose;
- does not prescribe;
- does not autonomously recommend treatment changes;
- surfaces potential medication-transition discrepancies for clinician review;
- requires evidence provenance before a finding is marked `VERIFIED`;
- can abstain when evidence is insufficient.

## Prior-work disclosure

SentinelRx is a separate UnivaBio competition codebase built from lessons learned in the earlier **FHIRGuard** medication-reconciliation safety prototype. The competition implementation adds a new clinician-facing workflow, evidence-provenance presentation, counterfactual testing, expanded benchmark coverage, explicit abstention behavior, and a polished end-to-end demo.

## Repository map

```text
sentinelrx/
├── sentinelrx/                  # core package + UI/API
├── scripts/                     # reproducible benchmark runners
├── tests/                       # regression + robustness tests
├── examples/                    # synthetic demo FHIR bundle
├── assets/
│   ├── sentinelrx-hero.png
│   └── SentinelRx_Judge_OnePager.pdf
├── benchmark_results.json
├── robust_benchmark_results.json
├── BENCHMARK_REPORT.md
├── ROBUSTNESS_REPORT.md
├── DEMO_SCRIPT.md
├── DEVPOST_GALLERY.md
└── SUBMISSION_CHECKLIST.md
```
