"""Separate candidate gate; verifies bundle-local predicates, never clinical truth."""
from collections import Counter
from .models import FindingType as T, VerificationStatus as S


def verify_candidate(finding, events):
    finding.verification_status = S.ABSTAIN
    finding.verification_reason = "Candidate predicate or evidence could not be established."
    if finding.finding_type == T.INSUFFICIENT_EVIDENCE:
        return finding
    index = {}
    counts = Counter((e.resource_type, e.resource_id) for e in events)
    for event in events:
        index[(event.resource_type, event.resource_id)] = event
    resolved = []
    for ref in finding.evidence:
        identity = (ref.resource_type, ref.resource_id)
        event = index.get(identity)
        if not ref.resource_id or counts[identity] != 1 or event is None:
            return finding
        if event.medication_key != finding.medication_key or ref.value != event.medication_display:
            return finding
        expected_role = {
            T.OMISSION: {"admission medication": "admission"},
            T.ADDITION: {"discharge medication": "discharge"},
            T.DUPLICATION: {"duplicate discharge entry": "discharge"},
            T.DOSE_CHANGE: {"admission dose": "admission", "discharge dose": "discharge"},
        }.get(finding.finding_type, {})
        if expected_role.get(ref.role) != event.context:
            return finding
        resolved.append(event)
    relevant = [e for e in events if e.medication_key == finding.medication_key or (e.medication_key == "unknown" and finding.finding_type in {T.OMISSION, T.ADDITION})]
    if any(e.issues or e.context == "unknown" or e.medication_key == "unknown" for e in relevant):
        finding.verification_reason = "Ambiguous or unsupported source data may affect this medication."
        return finding
    pre = [e for e in relevant if e.context == "admission"]
    post = [e for e in relevant if e.context == "discharge"]
    refs = {(e.resource_type, e.resource_id) for e in resolved}
    valid = False
    if finding.finding_type == T.OMISSION:
        valid = bool(pre) and not post and len(resolved) == 1
    elif finding.finding_type == T.ADDITION:
        valid = bool(post) and not pre and len(resolved) == 1
    elif finding.finding_type == T.DUPLICATION:
        valid = len(post) >= 2 and len(refs) == len(resolved) == len(post) and refs == {(e.resource_type, e.resource_id) for e in post}
    elif finding.finding_type == T.DOSE_CHANGE:
        before = {e.dose_text.strip().lower() for e in pre if e.dose_text}
        after = {e.dose_text.strip().lower() for e in post if e.dose_text}
        valid = (len(resolved) == len(refs) == 2 and {e.context for e in resolved} == {"admission", "discharge"}
                 and all(e.dose_text for e in pre + post) and len(before) == len(after) == 1 and before != after)
    if valid:
        finding.verification_status = S.VERIFIED
        finding.verification_reason = "Source identities, roles and bundle-local discrepancy predicate checked. Absence assumes the supplied lists are complete; clinical intent is not verified."
    return finding
