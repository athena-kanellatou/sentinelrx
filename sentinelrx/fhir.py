from __future__ import annotations
from collections.abc import Iterable
from typing import Any
from .models import MedicationEvent

SUPPORTED_MEDICATION_RESOURCES = {"MedicationRequest", "MedicationStatement"}

def iter_resources(bundle: dict[str, Any]) -> Iterable[dict[str, Any]]:
    if bundle.get("resourceType") != "Bundle":
        raise ValueError("Expected a FHIR Bundle")
    entries = bundle.get("entry", [])
    if not isinstance(entries, list):
        raise ValueError("FHIR Bundle.entry must be a list")
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        resource = entry.get("resource")
        if isinstance(resource, dict):
            yield resource

def patient_id(bundle: dict[str, Any]) -> str | None:
    for resource in iter_resources(bundle):
        if resource.get("resourceType") == "Patient":
            return resource.get("id")
    return None

def _coding_display(codeable):
    if not isinstance(codeable, dict):
        return ("unknown", "Unknown medication")
    coding = codeable.get("coding")
    if not isinstance(coding, list):
        return ("unknown", "Unknown medication")
    valid = [c for c in coding if isinstance(c, dict) and isinstance(c.get("code"), str) and c["code"].strip() and isinstance(c.get("system"), str) and c["system"].strip()]
    identities = {(c["system"].strip(), c["code"].strip()) for c in valid}
    if len(identities) != 1:
        return ("unknown", "Unknown medication")
    first = valid[0]
    return first["code"].strip(), str(first.get("display") or first["code"]).strip()


def _dose_text(resource):
    dosage = resource.get("dosageInstruction") or resource.get("dosage")
    if isinstance(dosage, list) and len(dosage) == 1 and isinstance(dosage[0], dict):
        text = dosage[0].get("text")
        return text.strip() if isinstance(text, str) and text.strip() else None
    return None


def infer_context(resource):
    meta = resource.get("meta")
    tags = meta.get("tag", []) if isinstance(meta, dict) else []
    roles = set()
    aliases = {"admission": "admission", "home": "admission", "pre": "admission", "discharge": "discharge", "post": "discharge"}
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, dict) and isinstance(tag.get("code"), str):
                role = aliases.get(tag["code"].strip().lower())
                if role:
                    roles.add(role)
    return next(iter(roles)) if len(roles) == 1 else "unknown"


def extract_medication_events(bundle):
    from collections import Counter, defaultdict
    events = []
    resources = list(iter_resources(bundle))
    patients = {r.get("id") for r in resources if r.get("resourceType") == "Patient" and isinstance(r.get("id"), str)}
    subjects = set()
    for r in resources:
        if r.get("resourceType") in ("MedicationRequest", "MedicationStatement"):
            subject = r.get("subject")
            if isinstance(subject, dict) and isinstance(subject.get("reference"), str):
                subjects.add(subject["reference"])
    mixed_subjects = len(patients) > 1 or len(subjects) > 1 or bool(patients and subjects and subjects != {"Patient/" + next(iter(patients))})
    systems = defaultdict(set)
    for resource in resources:
        rt = resource.get("resourceType")
        if not isinstance(rt, str) or rt not in SUPPORTED_MEDICATION_RESOURCES:
            continue
        medication = resource.get("medicationCodeableConcept")
        key, display = _coding_display(medication)
        if key != "unknown":
            systems[key].update(c["system"].strip() for c in medication["coding"] if isinstance(c, dict) and isinstance(c.get("system"), str) and c.get("code"))
        rid = resource.get("id")
        rid = rid.strip() if isinstance(rid, str) else ""
        issues = []
        if mixed_subjects:
            issues.append("Multiple or mismatched patient references; single-patient transition required.")
        if not rid:
            issues.append("Missing resource ID; provenance cannot be resolved.")
        status = resource.get("status")
        if status != "active":
            issues.append("Only explicitly active medication records are supported; status requires review.")
        if key == "unknown":
            issues.append("Medication identity needs one unambiguous system/code; text and references are unsupported.")
        context = infer_context(resource)
        if context == "unknown":
            issues.append("Missing or conflicting explicit transition tags.")
        dosage = resource.get("dosageInstruction") or resource.get("dosage")
        if isinstance(dosage, list) and len(dosage) > 1:
            issues.append("Multiple dosage instructions require review.")
        events.append(MedicationEvent(resource_type=rt, resource_id=rid,
            medication_key=key, medication_display=display,
            status=status if isinstance(status, str) else None,
            context=context, dose_text=_dose_text(resource), issues=issues))
    counts = Counter((e.resource_type, e.resource_id) for e in events)
    doses = defaultdict(set)
    for e in events:
        if e.dose_text:
            doses[(e.medication_key, e.context)].add(e.dose_text.strip().lower())
    for e in events:
        if len(doses[(e.medication_key, e.context)]) > 1:
            e.issues.append("Conflicting dose texts within one transition side require review.")
        if counts[(e.resource_type, e.resource_id)] > 1:
            e.issues.append("Repeated resource identity in bundle; cannot infer distinct prescriptions.")
        if len(systems[e.medication_key]) > 1:
            e.issues.append("Same code occurs in different terminology systems; identity is ambiguous.")
    return events
