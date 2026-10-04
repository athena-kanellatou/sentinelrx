# Local note classifier: model card

## Intended use

A reviewer manually associates ONE short synthetic English note with ONE medication. The model proposes a transition intent and a review question. It does not extract medication identity, normalize dosage, resolve discrepancies or validate clinical intent. No patient data leaves the process. The demo is for synthetic inputs only.

## Method and reproducibility

`note-triage-1`: scikit-learn 1.8.0, character word-boundary TF-IDF n-grams (3,5), logistic regression C=8, max_iter=1000, random_state=0. The model is fitted once per process from the packaged 48-example JSON, then cached. No downloaded weights, pickle or external inference is used. Source and training SHA-256 hashes travel with each proposal.

Four labels: stop, continue, change, start. Accept a proposal only if the top model score is at least 0.50 and its lead over the second class is at least 0.15. Simple guards abstain on explicit uncertainty, negation, questions and conjunctions. The thresholds were chosen before first scoring this evaluation file and not tuned afterwards. Guarded negative examples are an engineering policy, not learned negation understanding.

## Evaluation provenance

48 training sentences and 24 evaluation sentences were authored during the same implementation session. Evaluation sentences are excluded from fitting, but their author and domain vocabulary are shared. They are not a prospectively collected, externally authored or clinically held-out benchmark. Hashes, individual outputs and per-label statistics are in `note_ai_results.json`.

First measured result: 15/24 proposals (62.5% coverage), all 15 correct on this split; 23/24 exact outputs when abstention is a target label. One positive start note was abstained on. All eight examples labelled abstain were rejected. Always-abstain yields 8/24 exact outputs. Do not compare this task score with the record discrepancy F1; they measure different tasks.

## Failure modes

Tiny synthetic corpus; lexical overlap; no calibration; no clinical training; no long-note, multilingual, temporal, attribution or medication-entity reasoning. A confident incorrect proposal is possible. Novel uncertainty phrasing can evade guards. Conjunction/negation guards also over-abstain on valid text. The model may miss changes, and it cannot tell whether a note belongs to the selected medication or encounter.

## Safety architecture

The note endpoint receives text only and returns an unconfirmed proposal. The deterministic analysis endpoint never consumes it. No accepted note proposal changes an evidence badge, filters a discrepancy, writes FHIR, or executes an action. The UI explicitly displays the manually supplied medication link and exact source quote. The export is a demo annotation, not an authenticated clinician sign-off.

## Needed next evidence

Independent clinician-authored cases frozen before further model development; label disagreement review; negation and temporal challenge families; realistic encounter completeness; latency and workflow evaluation with intended users. These are outstanding work, not completed results.
