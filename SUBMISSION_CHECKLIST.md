# SentinelRx — Devpost Final Submission Checklist

## Project page order

### 1. Hero image
Upload first:
`assets/sentinelrx-hero.png`

### 2. Screenshot order
1. Safety Review
2. Medication Timeline
3. Evidence Provenance
4. Counterfactual Lab
5. Evaluation

### 3. Try it out
Add:
- public GitHub repository
- public hosted demo only if deployment is stable

Do not add a broken or temporary deployment link.

### 4. Video
Target length: 100–120 seconds.
Use `DEMO_SCRIPT.md`.

### 5. Judge PDF
Use:
`assets/SentinelRx_Judge_OnePager.pdf`

If Devpost does not have a dedicated PDF field, link it from the public GitHub repository README or project links.

## Claims audit

Safe:
- “identifies potential medication discrepancies for clinician review”
- “evidence-grounded”
- “synthetic FHIR R4 evaluation”
- “exact agreement with predefined ground truth on generated regression cases”
- “explicit abstention when evidence is insufficient”
- “0 crashes across 90 generated edge/incomplete cases”

Avoid:
- “prevents medication errors”
- “100% clinically accurate”
- “clinically validated”
- “safe for clinical deployment”
- “outperforms clinicians”
- “FDA-ready”
- “diagnoses”
- “prescribes”

## Metrics to show

Standard synthetic suite:
- 120 cases
- SentinelRx F1: 1.000
- Naive baseline F1: 0.600
- SentinelRx exact-case accuracy: 1.000
- Naive baseline exact-case accuracy: 0.500

Robustness suite:
- 90 cases
- verified-finding exact accuracy: 1.000
- abstention behavior accuracy: 1.000
- crash rate: 0.000

Always attach the qualifier:
“Generated synthetic test conditions only; not clinical validation.”

## Prior-work disclosure

Keep the prior-work paragraph visible in the Devpost “About” section. Do not remove it.

## Final pre-submit checks

- [ ] Public GitHub repo opens without authentication
- [ ] README renders correctly
- [ ] `pytest -q` passes
- [ ] hero image loads
- [ ] judge PDF opens
- [ ] benchmark JSON files are committed
- [ ] no API keys / secrets / `.env`
- [ ] no PHI or real patient data
- [ ] video link works in incognito/private browser
- [ ] all screenshots are readable on laptop screen
- [ ] Devpost About text matches actual implemented features
- [ ] sponsor prize claims are eligible
- [ ] Official Rules checkbox completed
- [ ] final submission completed before deadline
