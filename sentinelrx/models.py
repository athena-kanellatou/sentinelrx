from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class FindingType(str, Enum):
    OMISSION = "omission"
    ADDITION = "addition"
    DUPLICATION = "duplication"
    DOSE_CHANGE = "dose_change"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"

class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    ABSTAIN = "abstain"

class EvidenceRef(BaseModel):
    resource_type: str
    resource_id: str
    role: str
    path: str | None = None
    value: Any | None = None

class MedicationEvent(BaseModel):
    resource_type: str
    resource_id: str
    medication_key: str
    medication_display: str
    status: str | None = None
    context: str
    dose_text: str | None = None

class SafetyFinding(BaseModel):
    finding_id: str
    finding_type: FindingType
    medication_key: str
    medication_display: str
    summary: str
    rationale: str
    severity: str = "review"
    evidence: list[EvidenceRef] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.ABSTAIN

    def verify_if_grounded(self, minimum_evidence: int = 1) -> "SafetyFinding":
        self.verification_status = (
            VerificationStatus.VERIFIED if len(self.evidence) >= minimum_evidence
            else VerificationStatus.ABSTAIN
        )
        return self

class AnalysisResult(BaseModel):
    patient_id: str | None = None
    findings: list[SafetyFinding] = Field(default_factory=list)
    medications: list[MedicationEvent] = Field(default_factory=list)
