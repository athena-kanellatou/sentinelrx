# SentinelRx Demo Script (≈ 105 seconds)

## 0–12s — Problem
“Hospital discharge is a fragile transition. A medication can disappear, be duplicated, or change dose between admission and discharge.”

## 12–22s — Product
“SentinelRx is an evidence-grounded safety layer for medication transitions. The AI proposes. Deterministic code verifies. The clinician decides.”

## 22–45s — Safety Review
Open **Safety Review**.
Show verified findings and expand one.
Say: “A finding is never just text. It has to point back to evidence.”

## 45–60s — Evidence Provenance
Open **Evidence Graph**.
Show the FHIR resource IDs.
Say: “Every surfaced finding is traceable to the exact FHIR resources that support it.”

## 60–78s — Counterfactual
Open **Counterfactual Lab**.
Choose **Resolve metformin omission**.
Say: “Now I change the underlying synthetic evidence and rerun the same engine.”
Show that the omission disappears.

## 78–95s — Evaluation
Open **Evaluation**.
Show 120 standard cases and 90 robustness cases.
Say: “The benchmark is reproducible and synthetic. SentinelRx achieved exact agreement with predefined ground truth on the generated regression suite, while a simple medication-set baseline reached 0.600 F1.”

## 95–105s — Close
“SentinelRx is not trying to replace clinical judgment. It is designed to make AI-supported medication review more traceable, verifiable, and willing to abstain.”

Final screen:
**AI should not just produce an answer. It should be able to show the evidence behind it — or know when not to answer.**
