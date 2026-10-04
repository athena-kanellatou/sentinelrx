# SentinelRx: 115-second demo

0-10s — Show the admission/discharge timeline. “In this synthetic transition, metformin is absent from discharge, lisinopril appears twice, and its dose text changes.”

10-25s — Safety Review: 3 VERIFIED, 0 ABSTAIN, 4 resources. “SentinelRx flags discrepancies with deterministic rules. A separate gate checks the evidence before presenting verified findings for clinician review.”

25-43s — Expand the dose-text change and show both resource IDs and verification explanation. “Verified means these source references and the discrepancy predicate checked out within this bundle. It does not mean the change was clinically wrong.”

43-55s — Evidence Provenance table. “Each finding resolves to the records involved. No hidden source or generated clinical recommendation.”

55-75s — Counterfactual Lab: resolve metformin omission. Show three findings becoming two. “Changing the synthetic evidence removes the omission candidate when the same engine reruns.”

75-93s — Change Demo evidence to Missing medication identity; return to Safety Review. Show 0 VERIFIED and ABSTAIN explanations. “An unknown medication could change the comparison. The gate abstains instead of assuming it knows.”

93-108s — Evaluation: 120 regression, 90 failure-handling, 32 authored perturbations. “These are reproducible synthetic software tests, not held-out evaluation or clinical validation. The baseline only compares medication sets.”

108-115s — Close: “Evidence before confidence. Abstention before guessing. The clinician decides.”

Keep the scope caption visible. Do not describe this implementation as AI-powered, general FHIR support, clinical validation or an independent clinical verifier. Originality disclosure belongs in the submission text and README. Record actual UI footage; the hero graphic is an informational summary, not an application screenshot.
