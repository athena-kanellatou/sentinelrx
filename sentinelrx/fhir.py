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
    if not codeable:
        return ("unknown", "Unknown medication")
    coding = codeable.get("coding") or []
    if coding and isinstance(coding, list):
        first = coding[0] if isinstance(coding[0], dict) else {}
        key = str(first.get("code") or first.get("display") or "unknown").strip().lower()
        display = str(first.get("display") or first.get("code") or "Unknown medication").strip()
        return (key or "unknown", display or "Unknown medication")
    text = str(codeable.get("text") or "Unknown medication").strip()
    return (text.lower() or "unknown", text or "Unknown medication")

def _dose_text(resource):
    dosage = resource.get("dosageInstruction") or resource.get("dosage")
    if isinstance(dosage, list) and dosage:
        first = dosage[0] if isinstance(dosage[0], dict) else {}
        return str(first.get("text")) if first.get("text") else None
    if isinstance(dosage, dict):
        return str(dosage.get("text")) if dosage.get("text") else None
    return None

def infer_context(resource):
    tags = (resource.get("meta") or {}).get("tag") or []
    if isinstance(tags, list):
        for tag in tags:
            if not isinstance(tag, dict):
                continue
            combined = f"{tag.get('code','')} {tag.get('display','')}".lower()
            if any(x in combined for x in ("admission","home","pre")):
                return "admission"
            if any(x in combined for x in ("discharge","post")):
                return "discharge"
    return "unknown"

def extract_medication_events(bundle):
    events = []
    for resource in iter_resources(bundle):
        rt = resource.get("resourceType")
        if rt not in SUPPORTED_MEDICATION_RESOURCES:
            continue
        medication = resource.get("medicationCodeableConcept") or resource.get("medication") or {}
        key, display = _coding_display(medication)
        rid = str(resource.get("id") or "")
        if not rid:
            continue
        events.append(MedicationEvent(
            resource_type=rt,
            resource_id=rid,
            medication_key=key,
            medication_display=display,
            status=resource.get("status"),
            context=infer_context(resource),
            dose_text=_dose_text(resource),
        ))
    return events
