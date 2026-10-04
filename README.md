# SentinelRx

**Evidence-grounded medication-transition safety for synthetic FHIR R4 data**

> Rules flag discrepancies. Evidence checks gate findings. The clinician decides.

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
Resource parsing / structural checks
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

Create and activate an isolated virtual environment:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python -m streamlit run sentinelrx/ui.py
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

- 90 generated edge / incomplete synthetic cases
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

SentinelRx is a separate competition implementation in the same medication-transition safety problem family as [FHIRGuard](https://github.com/athena-kanellatou/fhirguard). The underlying reconciliation concept, provenance and abstention principles are prior work; these are not claimed as new inventions. This repository focuses on a lightweight interactive review workflow, explicit evidence states, counterfactual reruns and synthetic evaluation. The current revision adds a separate candidate verification gate and authored perturbation tests. This disclosure does not establish competition eligibility or claim that every feature first originated during the competition; build dates and any reused code should be checked against repository history and organizer rules.

## Verification contract and supported input

There is **no AI/LLM proposal layer** in this implementation. Candidate generation and verification are deterministic. `VERIFIED` means the candidate's references resolve uniquely to parsed supported records with consistent medication identity and context, and its discrepancy predicate holds **within the supplied bundle**. It does not establish clinical truth, prescribing appropriateness, or complete hospital data.

- Input is assumed to describe one patient and one transition. Conflicting explicit patient references trigger abstention; absent subjects and encounter chronology are not independently validated.
- Only active `MedicationRequest` and `MedicationStatement` records with non-empty IDs are supported.
- Identity requires one unambiguous `(system, code)` coding. Code case is preserved. Different terminology systems sharing a code trigger abstention; brand/generic and cross-code equivalence are not resolved. Text-only and medication-reference identity are unsupported and trigger abstention.
- Context uses exact `meta.tag.code` aliases: admission/home/pre or discharge/post. Conflicting tags trigger abstention. These are explicit project conventions, not inferred encounter chronology.
- Repeated IDs, ambiguous identity/context and unsupported statuses block affected verification. Unknown identity conservatively blocks all candidate verification.
- Omission/addition means absence from the supplied opposite list, **assuming both supplied lists are complete**; no encounter-level completeness or prescribing-intent proof is provided.
- Duplication requires distinct discharge resource identities; distinct records do not necessarily mean duplicate prescriptions in clinical practice.
- Dose changes compare trimmed, case-normalized text, not equivalent dosage semantics. Missing dose text is not assessed; multiple dosage instructions require review.
- The verifier is a separate predicate gate over the same parser output, not an independently implemented FHIR validator.

## Additional development challenges

```bash
python scripts/run_perturbation_benchmark.py
```

See `PERTURBATION_REPORT.md` and `perturbation_results.json`. These authored challenges exercise order/noise invariance, ambiguous provenance, terminology collisions, unsupported structures, conflicting context and candidate tampering tests. They were developed with the fixes, so are **not held-out or independent clinical validation**. The existing 120-case suite has six repeated pattern families, and the 90-case suite also repeats templates; case counts are not counts of independent clinical scenarios. The naive baseline is deliberately limited to set presence and is not a clinical or state-of-the-art comparator.

## What this prototype does not claim

No clinical validation, general FHIR conformance, medication appropriateness assessment, semantic dose equivalence, autonomous treatment decisions, learned AI inference or real-world safety performance. A clean result does not establish a safe discharge.

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
