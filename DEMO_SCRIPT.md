# Two-minute demo - record the current application

0:00-0:15 - Safety Review
“At discharge, an apparent missing medication can mean an error, an intended stop, or incomplete data. SentinelRx keeps these possibilities open for a reviewer.” Show the synthetic label and three evidence-checked findings.

0:15-0:30 - Evidence Provenance
“Each record finding links to the source. Evidence-checked means the local discrepancy predicate passed. It does not mean the prescription is clinically correct.” Expand the metformin omission and show its resource.

0:30-1:05 - AI Note Review
Select Metformin. Use Documented stop. “This real, local learned model reads a short synthetic note and proposes a stop. The original quote is visible. I linked it to metformin; the model has not verified that link. The omission remains on screen.” Select a reviewer annotation and download the audit JSON.

1:05-1:20 - AI abstention
Select Ambiguous instruction. “When the wording is uncertain, this model abstains. It cannot remove findings or approve a discharge.”

1:20-1:35 - Counterfactual Lab
Select Resolve metformin omission. “Only a change to the structured evidence changes the record finding. This control changes synthetic data, not a patient prescription.”

1:35-1:50 - Evaluation
“78 tests pass. The small authored note split had 23 of 24 correct outputs including abstentions, with only 15 proposals. We publish the failure as well. None of these are clinical validation.”

1:50-2:00 - Close
“FHIRGuard is disclosed prior work. SentinelRx adds a compact note-and-record review workflow: AI reads the note, rules check records, the reviewer decides.”

Use actual UI capture; do not reuse old footage showing VERIFIED or claiming there is no learned model. Do not claim clinical effectiveness, an independent held-out benchmark or a guaranteed score.
