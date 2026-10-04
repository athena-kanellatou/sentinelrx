"""Authored development challenges, NOT a held-out or clinical evaluation."""
from copy import deepcopy
from itertools import permutations
from .robust_benchmark import med, bundle, RobustCase, score_robust


def build_challenges():
    a = med('a', 'drug', 'Example', 'admission')
    d = med('d', 'drug', 'Example', 'discharge', '20 mg daily')
    cases = []
    def add(name, resources, expected=(), abstain=False):
        cases.append(RobustCase(name, bundle(name, deepcopy(resources)), {x.replace(":", ":urn:robust|", 1) if "|" not in x else x for x in expected}, abstain, name))
    noise = {'resourceType': 'Observation', 'id': 'noise'}
    for i, order in enumerate(permutations([a, d, noise])):
        add(f'order_noise_{i}', order, ['dose_change:drug'])
    x = deepcopy(d); x['medicationCodeableConcept']['coding'][0]['display'] = 'Alternative label'
    add('display_invariance', [a, x], ['dose_change:drug'])
    x = deepcopy(d); x['medicationCodeableConcept']['coding'].insert(0, {})
    add('blank_first_coding', [a, x], ['dose_change:drug'])
    x = deepcopy(d); x['meta']['tag'][0]['code'] = ' DISCHARGE '
    add('context_case_space', [a, x], ['dose_change:drug'])
    x = deepcopy(a); x['resourceType'] = 'MedicationStatement'; x['dosage'] = x.pop('dosageInstruction')
    add('mixed_resource_types', [x, d], ['dose_change:drug'])
    for field, value in [('id', ''), ('status', 'stopped'), ('status', 'cancelled'), ('status', None), ('meta', 'invalid')]:
        x = deepcopy(d); x[field] = value
        add(f'invalid_{field}_{value}', [a, x], [], True)
    add('repeated_discharge_id', [a, d, d], [], True)
    add('repeated_admission_id', [a, a, d], [], True)
    x = deepcopy(d); x['meta']['tag'].append({'code': 'admission'})
    add('conflicting_tags', [a, x], [], True)
    x = deepcopy(d); x['meta']['tag'] = [{'code': 'postoperative'}]
    add('substring_is_not_context', [a, x], [], True)
    x = deepcopy(d); x['medicationCodeableConcept']['coding'][0]['system'] = 'urn:other'
    add('distinct_systems', [a, x], ['omission:urn:robust|drug', 'addition:urn:other|drug'])
    x = deepcopy(d); x['medicationCodeableConcept']['coding'].append({'system': 'urn:other', 'code': 'other'})
    add('ambiguous_codings', [a, x], [], True)
    for value in ['broken', {'text': 'Example'}, {'coding': 'bad'}, {'coding': [None]}, {}]:
        x = deepcopy(d); x['medicationCodeableConcept'] = value
        add(f'malformed_identity_{len(cases)}', [a, x], [], True)
    x = deepcopy(d); x.pop('medicationCodeableConcept'); x['medicationReference'] = {'reference': 'Medication/drug'}
    add('unsupported_reference', [a, x], [], True)
    x = deepcopy(d); x['dosageInstruction'].append({'text': 'additional schedule'})
    add('multiple_dosages', [a, x], [], True)
    x = deepcopy(d); x['dosageInstruction'] = [{'text': ' 10 MG DAILY '}]
    add('dose_case_space', [a, x])
    x = deepcopy(d); x['dosageInstruction'] = [{'text': '10mg q24h'}]
    add('dose_text_not_semantic_equivalence', [a, x], ['dose_change:drug'])
    x = deepcopy(d); x.pop('dosageInstruction')
    add('missing_dose_no_dose_claim', [a, x])
    x = deepcopy(a); x['id'] = 'a2'; x['dosageInstruction'] = [{'text': '30 mg daily'}]
    add('conflicting_admission_doses', [a, x, d], [], True)
    return cases


def run_challenges():
    return {'evaluation_scope': 'Authored development perturbations; not held-out, independently labelled, or clinically validated.', **score_robust(build_challenges())}
