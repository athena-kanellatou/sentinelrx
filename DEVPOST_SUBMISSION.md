# SentinelRx

## Tagline
AI-assisted medication review that keeps source evidence and uncertainty visible.

## Inspiration
A medication missing from a discharge list could be an error, an intentional stop, or incomplete information. A fluent AI answer cannot settle that distinction. We built a workspace where a reviewer can compare a learned interpretation of a short note with the medication records and retain the evidence for follow-up.

## What it does
SentinelRx flags potential omissions, additions, duplicate records and dose-text changes in synthetic FHIR R4-shaped medication lists. A separate gate checks references and bundle-local predicates. The interface says EVIDENCE-CHECKED or ABSTAIN, not clinically verified.

A local learned model proposes whether a short note describes stopping, continuing, changing or starting a medication. Low-separation or unsupported language triggers abstention. The reviewer supplies the medication link, sees the exact quote beside the record discrepancy, records a demo annotation and downloads an audit JSON. AI never hides or resolves a record finding.

## How we built it
Python, scikit-learn character TF-IDF and logistic regression, Pydantic, FastAPI and Streamlit. The model learns from 48 published synthetic examples and runs locally without a model API key. The record path uses namespace-safe medication identities, explicit source references, patient/order checks and deterministic predicates. Counterfactual controls show what changes when the underlying synthetic records change.

## What we tested
78 automated tests pass. The note classifier produced 23/24 correct outputs including abstentions on an author-written synthetic evaluation split excluded from training. It made 15 proposals, all correct on that small split, and abstained on nine notes, including one labelled positive. These are development results, not clinical accuracy. The repository publishes every prediction and the data hashes.

The deterministic path also matches expected outputs on 120 generated regression cases, 90 edge/incomplete cases and 32 authored perturbations. Those repeat known patterns and do not establish clinical generalization. A set-only baseline lacks dose-change and duplicate detection, so its lower F1 is a limited engineering comparison.

## Challenges and limitations
Record absence depends on supplied-list completeness; transition sides use explicit project tags, not reconstructed encounters. Dose comparison is textual. The gate shares the parser with detection. The small note classifier does not understand all negation, temporal context or clinical intent and may produce wrong proposals. A model score is not calibrated confidence. No clinical deployment, effectiveness or safe-discharge claim is made.

## Prior work
My earlier FHIRGuard project explores the same reconciliation, provenance and abstention principles, including constrained model use. Those concepts are prior work. SentinelRx is a separate compact implementation focused on interactive review. This revision adds a local learned note classifier, source-hashed review exports, the manually linked note/record workspace and stricter input checks. Repository history documents the implementation dates.

## What is next
Independent clinician-authored evaluation; richer encounter and list semantics; calibrated abstention; and measured usability with intended reviewers. These are planned, not finished.
