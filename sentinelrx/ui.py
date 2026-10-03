
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from sentinelrx.engine import analyze_bundle
from sentinelrx.models import VerificationStatus


ROOT = Path(__file__).resolve().parents[1]
STANDARD_RESULTS = ROOT / "benchmark_results.json"
ROBUST_RESULTS = ROOT / "robust_benchmark_results.json"
DEMO_BUNDLE = ROOT / "examples" / "demo_bundle.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def metric_card(label: str, value: str, help_text: str | None = None):
    st.metric(label, value, help=help_text)


def evidence_table(findings):
    rows = []
    for finding in findings:
        for ev in finding.evidence:
            rows.append({
                "Finding": finding.summary,
                "Status": finding.verification_status.value.upper(),
                "FHIR Resource": f"{ev.resource_type}/{ev.resource_id}",
                "Evidence role": ev.role,
                "Value": ev.value,
            })
    return pd.DataFrame(rows)


def medication_table(result):
    return pd.DataFrame([
        {
            "Medication": m.medication_display,
            "Context": m.context,
            "Dose": m.dose_text or "—",
            "FHIR Resource": f"{m.resource_type}/{m.resource_id}",
        }
        for m in result.medications
    ])


def mutate_bundle(bundle: dict, mode: str) -> dict:
    data = json.loads(json.dumps(bundle))
    entries = data.get("entry", [])
    resources = [e.get("resource", {}) for e in entries if isinstance(e, dict)]

    if mode == "Resolve metformin omission":
        source = next((r for r in resources if r.get("id") == "home-metformin"), None)
        if source:
            clone = json.loads(json.dumps(source))
            clone["id"] = "discharge-metformin"
            clone.setdefault("meta", {})["tag"] = [{"code": "discharge"}]
            entries.append({"resource": clone})

    elif mode == "Remove duplicate lisinopril":
        data["entry"] = [
            e for e in entries
            if not (isinstance(e, dict) and isinstance(e.get("resource"), dict)
                    and e["resource"].get("id") == "discharge-lisinopril-copy")
        ]

    elif mode == "Revert lisinopril dose change":
        for r in resources:
            if r.get("id") in {"discharge-lisinopril", "discharge-lisinopril-copy"}:
                r["dosageInstruction"] = [{"text": "10 mg daily"}]

    return data


st.set_page_config(page_title="SentinelRx", page_icon="🛡️", layout="wide")

st.title("SentinelRx")
st.caption("Evidence-grounded medication-transition safety for synthetic FHIR R4 data")

st.info("The AI proposes. Deterministic code verifies. The clinician decides.")

bundle = load_json(DEMO_BUNDLE)
result = analyze_bundle(bundle)

tabs = st.tabs([
    "Safety Review",
    "Medication Timeline",
    "Evidence Graph",
    "Counterfactual Lab",
    "Evaluation",
])

with tabs[0]:
    st.subheader("Discharge Safety Review")
    verified = [f for f in result.findings if f.verification_status == VerificationStatus.VERIFIED]
    abstained = [f for f in result.findings if f.verification_status == VerificationStatus.ABSTAIN]

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Verified findings", str(len(verified)))
    with c2:
        metric_card("Abstentions", str(len(abstained)))
    with c3:
        metric_card("FHIR resources reviewed", str(len(result.medications)))

    if not result.findings:
        st.success("No discrepancies detected.")
    else:
        for finding in result.findings:
            status = "VERIFIED" if finding.verification_status == VerificationStatus.VERIFIED else "ABSTAIN"
            with st.expander(f"{status} · {finding.summary}", expanded=True):
                st.write(finding.rationale)
                st.caption(f"Finding type: {finding.finding_type.value}")
                st.write("Evidence")
                for ev in finding.evidence:
                    st.code(f"{ev.resource_type}/{ev.resource_id}  ·  {ev.role}")

with tabs[1]:
    st.subheader("Admission → Discharge Medication Timeline")
    df = medication_table(result)
    if not df.empty:
        st.dataframe(df, width="stretch", hide_index=True)
        pivot = (
            df.assign(Present="●")
              .pivot_table(index="Medication", columns="Context", values="Present", aggfunc="first", fill_value="")
              .reset_index()
        )
        st.write("Transition view")
        st.dataframe(pivot, width="stretch", hide_index=True)

with tabs[2]:
    st.subheader("Evidence Provenance")
    st.write("Every surfaced finding must link back to concrete FHIR resources.")
    ev = evidence_table(result.findings)
    if ev.empty:
        st.info("No evidence links to show.")
    else:
        st.dataframe(ev, width="stretch", hide_index=True)
        st.caption("This is the core safety contract: no unsupported finding reaches VERIFIED state.")

with tabs[3]:
    st.subheader("Counterfactual Safety Lab")
    st.write("Change a synthetic clinical fact and rerun the exact same engine.")
    mode = st.selectbox(
        "Scenario",
        [
            "Resolve metformin omission",
            "Remove duplicate lisinopril",
            "Revert lisinopril dose change",
        ],
    )
    mutated = mutate_bundle(bundle, mode)
    mutated_result = analyze_bundle(mutated)

    left, right = st.columns(2)
    with left:
        st.markdown("**Before**")
        for f in result.findings:
            st.write(f"• {f.summary}")
    with right:
        st.markdown("**After**")
        if mutated_result.findings:
            for f in mutated_result.findings:
                st.write(f"• {f.summary}")
        else:
            st.success("No remaining discrepancies in this scenario.")

    before_ids = {f.finding_id for f in result.findings}
    after_ids = {f.finding_id for f in mutated_result.findings}
    resolved = sorted(before_ids - after_ids)
    if resolved:
        st.success("Resolved by changed evidence: " + ", ".join(resolved))

with tabs[4]:
    st.subheader("Reproducible Evaluation")
    std = load_json(STANDARD_RESULTS)
    robust = load_json(ROBUST_RESULTS)

    a = std["sentinelrx"]
    b = std["naive_baseline"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Synthetic regression cases", str(a["cases"]))
    with c2:
        metric_card("SentinelRx F1", f'{a["f1"]:.3f}')
    with c3:
        metric_card("Naive baseline F1", f'{b["f1"]:.3f}')
    with c4:
        metric_card("Robust crash rate", f'{robust["crash_rate"]:.3f}')

    st.write("Standard benchmark")
    st.dataframe(pd.DataFrame([
        {"System": "SentinelRx", "Precision": a["precision"], "Recall": a["recall"], "F1": a["f1"], "Exact-case accuracy": a["exact_case_accuracy"]},
        {"System": "Naive baseline", "Precision": b["precision"], "Recall": b["recall"], "F1": b["f1"], "Exact-case accuracy": b["exact_case_accuracy"]},
    ]), width="stretch", hide_index=True)

    st.write("Failure-handling benchmark")
    st.dataframe(pd.DataFrame([{
        "Cases": robust["cases"],
        "Verified exact accuracy": robust["verified_exact_accuracy"],
        "Abstention behavior accuracy": robust["abstention_behavior_accuracy"],
        "Crash rate": robust["crash_rate"],
    }]), width="stretch", hide_index=True)

    st.warning(
        "These results measure deterministic behavior on generated synthetic test conditions. "
        "They are not clinical validation and should not be interpreted as real-world clinical performance."
    )

st.divider()
st.caption("Synthetic data only · Clinical decision support prototype · No autonomous diagnosis or prescribing")
