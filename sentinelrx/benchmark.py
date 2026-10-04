from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .engine import analyze_bundle

MEDS = [
    ("metformin","Metformin"),
    ("lisinopril","Lisinopril"),
    ("amlodipine","Amlodipine"),
    ("atorvastatin","Atorvastatin"),
    ("omeprazole","Omeprazole"),
    ("aspirin","Aspirin"),
]

def med(rid, code, display, context, dose="10 mg daily"):
    return {
        "resourceType":"MedicationRequest",
        "id":rid,
        "status":"active",
        "intent":"order",
        "meta":{"tag":[{"code":context}]},
        "medicationCodeableConcept":{"coding":[{"system":"urn:sentinelrx","code":code,"display":display}]},
        "dosageInstruction":[{"text":dose}],
    }

def bundle(case_id, meds):
    from copy import deepcopy
    meds = deepcopy(meds)
    for resource in meds:
        if resource.get("resourceType") in {"MedicationRequest", "MedicationStatement"}:
            resource.setdefault("subject", {"reference": "Patient/" + case_id})
    return {
        "resourceType":"Bundle",
        "type":"collection",
        "entry":[{"resource":{"resourceType":"Patient","id":case_id}}] + [{"resource":m} for m in meds],
    }

@dataclass
class Case:
    case_id: str
    bundle: dict
    expected: set[str]
    category: str

def build_cases(n=120):
    cases=[]
    idx=1
    patterns=["clean","omission","addition","duplication","dose_change","mixed"]
    for i in range(n):
        category=patterns[i % len(patterns)]
        a_code,a_disp = MEDS[(i*2) % len(MEDS)]
        b_code,b_disp = MEDS[(i*2+1) % len(MEDS)]
        meds=[]
        expected=set()
        if category=="clean":
            meds += [med(f"a-{idx}",a_code,a_disp,"admission"), med(f"d-{idx}",a_code,a_disp,"discharge")]
        elif category=="omission":
            meds += [med(f"a-{idx}",a_code,a_disp,"admission")]
            expected.add(f"omission:{a_code}")
        elif category=="addition":
            meds += [med(f"d-{idx}",a_code,a_disp,"discharge")]
            expected.add(f"addition:{a_code}")
        elif category=="duplication":
            meds += [med(f"a-{idx}",a_code,a_disp,"admission"),
                     med(f"d1-{idx}",a_code,a_disp,"discharge"),
                     med(f"d2-{idx}",a_code,a_disp,"discharge")]
            expected.add(f"duplication:{a_code}")
        elif category=="dose_change":
            meds += [med(f"a-{idx}",a_code,a_disp,"admission","10 mg daily"),
                     med(f"d-{idx}",a_code,a_disp,"discharge","20 mg daily")]
            expected.add(f"dose_change:{a_code}")
        else:
            meds += [med(f"a1-{idx}",a_code,a_disp,"admission"),
                     med(f"a2-{idx}",b_code,b_disp,"admission"),
                     med(f"d1-{idx}",a_code,a_disp,"discharge","20 mg daily"),
                     med(f"d2-{idx}",a_code,a_disp,"discharge","20 mg daily")]
            expected.add(f"omission:{b_code}")
            expected.add(f"dose_change:{a_code}")
            expected.add(f"duplication:{a_code}")
        cases.append(Case(f"SRX-{idx:03d}", bundle(f"SRX-{idx:03d}", meds), {x.replace(":", ":urn:sentinelrx|", 1) for x in expected}, category))
        idx += 1
    return cases

def sentinel_predict(case):
    return {f.finding_id for f in analyze_bundle(case.bundle).findings if f.verification_status.value == "verified"}

def naive_baseline_predict(case):
    # Deliberately simple baseline: compare med presence only; cannot handle duplicates or dose changes.
    admissions=set()
    discharges=set()
    for e in case.bundle["entry"]:
        r=e["resource"]
        if r.get("resourceType")!="MedicationRequest":
            continue
        coding=r["medicationCodeableConcept"]["coding"][0]
        code=coding["system"] + "|" + coding["code"]
        context=r.get("meta",{}).get("tag",[{}])[0].get("code")
        if context=="admission":
            admissions.add(code)
        elif context=="discharge":
            discharges.add(code)
    out={f"omission:{x}" for x in admissions-discharges}
    out |= {f"addition:{x}" for x in discharges-admissions}
    return out

def score(cases, predictor: Callable[[Case], set[str]]):
    tp=fp=fn=0
    exact=0
    total_pred=0
    total_expected=0
    by_category={}
    for case in cases:
        pred=predictor(case)
        gold=case.expected
        total_pred += len(pred)
        total_expected += len(gold)
        tp += len(pred & gold)
        fp += len(pred - gold)
        fn += len(gold - pred)
        exact += int(pred == gold)
        bucket=by_category.setdefault(case.category, {"cases":0,"exact":0})
        bucket["cases"] += 1
        bucket["exact"] += int(pred==gold)
    precision = tp/(tp+fp) if tp+fp else 1.0
    recall = tp/(tp+fn) if tp+fn else 1.0
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {
        "cases":len(cases),
        "tp":tp,"fp":fp,"fn":fn,
        "precision":precision,
        "recall":recall,
        "f1":f1,
        "exact_case_accuracy":exact/len(cases) if cases else 0.0,
        "avg_predictions":total_pred/len(cases) if cases else 0.0,
        "avg_expected":total_expected/len(cases) if cases else 0.0,
        "by_category":{k:{**v,"exact_case_accuracy":v["exact"]/v["cases"]} for k,v in by_category.items()},
    }

def run_benchmark(n=120):
    cases=build_cases(n)
    return {
        "sentinelrx":score(cases, sentinel_predict),
        "naive_baseline":score(cases, naive_baseline_predict),
    }
