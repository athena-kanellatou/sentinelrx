from __future__ import annotations
from dataclasses import dataclass
from .engine import analyze_bundle
from .models import VerificationStatus

def med(rid, code=None, display=None, context=None, dose="10 mg daily"):
    r = {"resourceType":"MedicationRequest","id":rid,"status":"active","intent":"order"}
    if context is not None:
        r["meta"]={"tag":[{"code":context}]}
    if code is not None or display is not None:
        r["medicationCodeableConcept"]={"coding":[{"system":"urn:robust","code":code,"display":display}]}
    if dose is not None:
        r["dosageInstruction"]=[{"text":dose}]
    return r

def bundle(cid, resources):
    return {"resourceType":"Bundle","type":"collection",
            "entry":[{"resource":{"resourceType":"Patient","id":cid}}] + [{"resource":r} for r in resources]}

@dataclass
class RobustCase:
    case_id: str
    payload: dict
    expected_verified: set[str]
    expect_abstain: bool
    category: str

def build_robust_cases():
    cases=[]
    i=1
    def add(category, resources, expected=None, abstain=False, payload=None):
        nonlocal i
        cid=f"RB-{i:03d}"
        cases.append(RobustCase(cid, payload if payload is not None else bundle(cid, resources),
                                set(expected or []), abstain, category))
        i+=1

    meds=[("metformin","Metformin"),("lisinopril","Lisinopril"),("amlodipine","Amlodipine")]
    for j in range(15):
        c,d=meds[j%3]; add("clean",[med(f"a{j}",c,d,"admission"),med(f"d{j}",c,d,"discharge")])
    for j in range(15):
        c,d=meds[j%3]; add("omission",[med(f"a{j}",c,d,"admission")],[f"omission:{c}"])
    for j in range(10):
        c,d=meds[j%3]; add("unknown_context",[med(f"u{j}",c,d,None)],[],True)
    for j in range(10):
        add("unknown_medication",[med(f"u{j}",None,None,"admission")],[],True)
    for j in range(10):
        c,d=meds[j%3]
        add("missing_dosage",[med(f"a{j}",c,d,"admission",None),med(f"d{j}",c,d,"discharge","20 mg daily")],[])
    for j in range(10):
        c,d=meds[j%3]
        add("duplicate",[med(f"a{j}",c,d,"admission"),med(f"d1{j}",c,d,"discharge"),med(f"d2{j}",c,d,"discharge")],[f"duplication:{c}"])
    for j in range(10):
        c,d=meds[j%3]
        add("dose_change",[med(f"a{j}",c,d,"admission","10 mg daily"),med(f"d{j}",c,d,"discharge","20 mg daily")],[f"dose_change:{c}"])
    for j in range(10):
        cid=f"RB-{i:03d}"
        payload={"resourceType":"Bundle","type":"collection","entry":[
            {"resource":{"resourceType":"Patient","id":cid}}, {}, {"resource":"not-a-dict"},
            {"resource":{"resourceType":"Observation","id":f"o{j}"}}]}
        add("malformed_entries",[],[],False,payload)
    return cases

def score_robust(cases):
    verified_exact=0; abstain_correct=0; crashes=0; rows=[]
    for c in cases:
        try:
            result=analyze_bundle(c.payload)
            verified={f.finding_id for f in result.findings if f.verification_status==VerificationStatus.VERIFIED}
            abstain=any(f.verification_status==VerificationStatus.ABSTAIN for f in result.findings)
            v_ok=verified==c.expected_verified
            a_ok=abstain==c.expect_abstain
            verified_exact += int(v_ok); abstain_correct += int(a_ok)
            rows.append({"case":c.case_id,"category":c.category,"verified_exact":v_ok,"abstain_correct":a_ok})
        except Exception as e:
            crashes+=1; rows.append({"case":c.case_id,"category":c.category,"error":type(e).__name__})
    n=len(cases)
    return {"cases":n,
            "verified_exact_accuracy":verified_exact/n,
            "abstention_behavior_accuracy":abstain_correct/n,
            "crash_rate":crashes/n,
            "crashes":crashes,
            "rows":rows}

def run_robust_benchmark():
    return score_robust(build_robust_cases())
