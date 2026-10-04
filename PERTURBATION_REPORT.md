# Authored development perturbations

These 32 challenges were authored during verifier hardening. They are NOT held-out, externally labelled, independent of development, or clinical validation. Six cases are permutations of one transition plus irrelevant Observation noise; the case count must not imply 32 independent clinical scenarios.

Run `python scripts/run_perturbation_benchmark.py` to regenerate `perturbation_results.json`.

Current result: exact verified-finding sets 32/32; expected abstention presence 32/32; crashes 0/32. Separate pytest tests attempt to forge candidate evidence and ensure a previously verified candidate is rechecked.

Coverage: resource order/noise, display invariance, blank first coding, normalized context tags, mixed supported resource types, missing ID, repeated IDs, unsupported statuses, malformed metadata and medication coding, distinct terminology systems sharing one code, conflicting context, unsupported medication references, multiple dosage instructions, missing dose and contradictory admission doses.

Expected behavior is explicit in `sentinelrx/perturbation.py`; it is not obtained by running the engine to generate labels. However the cases and implementation were developed together, so they remain regression evidence. Dose synonyms deliberately produce a dose-TEXT finding: semantic dose equivalence is not supported. Missing dose text is not assessed and does not by itself produce an abstention.

Remaining limits: no externally reviewed clinical cases, encounter completeness proof, terminology mapping, real-world FHIR conformance testing, clinical intent assessment or performance comparison with a clinical reconciliation system. Abstention accuracy measures the presence of any abstention, not the clinical quality of its rationale or calibration.
