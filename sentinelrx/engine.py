from collections import Counter, defaultdict
from .fhir import extract_medication_events, patient_id
from .models import AnalysisResult, EvidenceRef, FindingType, SafetyFinding, VerificationStatus

def _evidence(event, role):
    return EvidenceRef(resource_type=event.resource_type, resource_id=event.resource_id, role=role, value=event.medication_display)

def _group(events, context):
    grouped = defaultdict(list)
    for event in events:
        if event.context == context:
            grouped[event.medication_key].append(event)
    return grouped

def detect_candidates(events):
    findings = []

    for event in events:
        if event.context == "unknown" or event.medication_key == "unknown":
            findings.append(SafetyFinding(
                finding_id=f"abstain:{event.resource_id}",
                finding_type=FindingType.INSUFFICIENT_EVIDENCE,
                medication_key=event.medication_key,
                medication_display=event.medication_display,
                summary=f"Insufficient evidence for {event.medication_display}",
                rationale="Medication resource lacks reliable transition context or medication identity.",
                evidence=[_evidence(event, "unresolved medication resource")],
                verification_status=VerificationStatus.ABSTAIN,
            ))

    usable = [e for e in events if e.context in {"admission","discharge"} and e.medication_key != "unknown"]
    admission = _group(usable, "admission")
    discharge = _group(usable, "discharge")

    for key in sorted(set(admission) - set(discharge)):
        src = admission[key][0]
        findings.append(SafetyFinding(
            finding_id=f"omission:{key}", finding_type=FindingType.OMISSION,
            medication_key=key, medication_display=src.medication_display,
            summary=f"Potential unexplained omission: {src.medication_display}",
            rationale="Medication appears in admission/home list but not discharge list.",
            evidence=[_evidence(src, "admission medication")]
        ).verify_if_grounded())

    for key in sorted(set(discharge) - set(admission)):
        src = discharge[key][0]
        findings.append(SafetyFinding(
            finding_id=f"addition:{key}", finding_type=FindingType.ADDITION,
            medication_key=key, medication_display=src.medication_display,
            summary=f"Potential new medication at discharge: {src.medication_display}",
            rationale="Medication appears in discharge list but not admission/home list.",
            evidence=[_evidence(src, "discharge medication")]
        ).verify_if_grounded())

    counts = Counter(e.medication_key for e in usable if e.context == "discharge")
    for key,count in counts.items():
        if count >= 2:
            dup = discharge[key]
            findings.append(SafetyFinding(
                finding_id=f"duplication:{key}", finding_type=FindingType.DUPLICATION,
                medication_key=key, medication_display=dup[0].medication_display,
                summary=f"Potential duplicate discharge medication: {dup[0].medication_display}",
                rationale=f"{count} discharge resources resolve to same medication key.",
                evidence=[_evidence(e, "duplicate discharge entry") for e in dup]
            ).verify_if_grounded(minimum_evidence=2))

    for key in sorted(set(admission) & set(discharge)):
        pre, post = admission[key][0], discharge[key][0]
        if pre.dose_text and post.dose_text and pre.dose_text.strip().lower() != post.dose_text.strip().lower():
            findings.append(SafetyFinding(
                finding_id=f"dose_change:{key}", finding_type=FindingType.DOSE_CHANGE,
                medication_key=key, medication_display=post.medication_display,
                summary=f"Dose text changed for {post.medication_display}",
                rationale=f"Admission dose: '{pre.dose_text}' -> discharge dose: '{post.dose_text}'.",
                evidence=[_evidence(pre, "admission dose"), _evidence(post, "discharge dose")]
            ).verify_if_grounded(minimum_evidence=2))
    return findings

def analyze_bundle(bundle):
    events = extract_medication_events(bundle)
    return AnalysisResult(patient_id=patient_id(bundle), medications=events, findings=detect_candidates(events))
