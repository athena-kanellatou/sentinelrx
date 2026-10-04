from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from sentinelrx.api import app, MAX_BODY_BYTES
from sentinelrx.engine import analyze_bundle
from sentinelrx.fhir import medication_identity
from sentinelrx.robust_benchmark import med, bundle


def pair():
    return bundle('p', [med('a','drug','Drug','admission'), med('d','drug','Drug','discharge','20 mg daily')])


def checked(result):
    return [f for f in result.findings if f.verification_status.value == 'verified']


def test_namespace_is_part_of_identity_and_separator_is_escaped():
    data = pair()
    data['entry'][2]['resource']['medicationCodeableConcept']['coding'][0]['system'] = 'urn:other'
    findings = checked(analyze_bundle(data))
    assert {f.finding_type.value for f in findings} == {'addition','omission'}
    assert len({f.medication_key for f in findings}) == 2
    assert medication_identity('urn:a|b', 'c') != medication_identity('urn:a','b|c')


@pytest.mark.parametrize('field,value', [('subject',None),('intent','proposal'),('doNotPerform',True),
                                        ('modifierExtension',[{'url':'urn:unknown','valueBoolean':True}]),
                                        ('priorPrescription',{'reference':'MedicationRequest/old'})])
def test_unsupported_source_cannot_pass(field,value):
    data=pair(); data['entry'][2]['resource'][field]=value
    assert not checked(analyze_bundle(data))


def test_unknown_identity_does_not_block_positive_unrelated_predicate():
    data=pair()
    unknown=med('u',None,None,'discharge'); unknown['subject']={'reference':'Patient/p'}
    data['entry'].append({'resource':unknown})
    findings=analyze_bundle(data).findings
    assert any(f.finding_type.value=='dose_change' and f.verification_status.value=='verified' for f in findings)
    assert any(f.verification_status.value=='abstain' for f in findings)


def test_unknown_identity_still_blocks_absence_claims():
    data=pair(); data['entry'][2]['resource'].pop('medicationCodeableConcept')
    assert not checked(analyze_bundle(data))


@pytest.mark.parametrize('entries',[None,[None],[{}],[{'resource':'bad'}]])
def test_invalid_bundle_entries_are_explicit_errors(entries):
    data=pair(); data['entry']=entries
    assert TestClient(app).post('/analyze',json=data).status_code==400


def test_api_bounds_real_body_and_rejects_unsupported_bundle():
    client=TestClient(app)
    assert client.post('/analyze',content=b' '*(MAX_BODY_BYTES+1)).status_code==413
    data=pair(); data['type']='transaction'
    assert client.post('/analyze',json=data).status_code==400
