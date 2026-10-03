from copy import deepcopy
import pytest
from sentinelrx.engine import analyze_bundle, detect_candidates
from sentinelrx.fhir import extract_medication_events
from sentinelrx.models import VerificationStatus as S
from sentinelrx.perturbation import build_challenges
from sentinelrx.robust_benchmark import med, bundle
from sentinelrx.verifier import verify_candidate


@pytest.mark.parametrize('case', build_challenges(), ids=lambda c: c.case_id)
def test_authored_challenge(case):
    result = analyze_bundle(case.payload)
    assert {f.finding_id for f in result.findings if f.verification_status == S.VERIFIED} == case.expected_verified
    assert any(f.verification_status == S.ABSTAIN for f in result.findings) == case.expect_abstain


def candidate():
    events = extract_medication_events(bundle('p', [med('a', 'drug', 'Drug', 'admission'), med('d', 'drug', 'Drug', 'discharge', '20 mg daily')]))
    return detect_candidates(events)[0], events


@pytest.mark.parametrize('mutation', ['missing_id', 'wrong_role', 'wrong_key', 'repeat_ref', 'false_type'])
def test_forged_candidate_rejected(mutation):
    f, events = candidate()
    if mutation == 'missing_id': f.evidence[0].resource_id = 'nonexistent'
    if mutation == 'wrong_role': f.evidence[0].role = 'discharge dose'
    if mutation == 'wrong_key': f.medication_key = 'other'
    if mutation == 'repeat_ref': f.evidence[1] = deepcopy(f.evidence[0])
    if mutation == 'false_type': f.finding_type = 'omission'
    assert verify_candidate(f, events).verification_status == S.ABSTAIN


def test_candidates_are_untrusted_and_verification_recomputed():
    f, events = candidate()
    assert f.verification_status == S.ABSTAIN
    assert verify_candidate(f, events).verification_status == S.VERIFIED
    f.evidence.clear()
    assert verify_candidate(f, events).verification_status == S.ABSTAIN


def test_mixed_patient_bundle_cannot_verify():
    a = med('a', 'drug', 'Drug', 'admission')
    d = med('d', 'drug', 'Drug', 'discharge', '20 mg daily')
    a['subject'] = {'reference': 'Patient/p'}
    d['subject'] = {'reference': 'Patient/another'}
    result = analyze_bundle(bundle('p', [a, d]))
    assert result.findings
    assert all(f.verification_status == S.ABSTAIN for f in result.findings)


@pytest.mark.parametrize('reverse', [False, True])
def test_conflicting_doses_abstain_even_when_first_pair_matches(reverse):
    rows = [med('a1', 'drug', 'Drug', 'admission'),
            med('a2', 'drug', 'Drug', 'admission', '20 mg daily'),
            med('d', 'drug', 'Drug', 'discharge')]
    if reverse: rows.reverse()
    result = analyze_bundle(bundle('p', rows))
    assert result.findings
    assert all(f.verification_status == S.ABSTAIN for f in result.findings)
