
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from sentinelrx.engine import analyze_bundle
from sentinelrx.models import VerificationStatus
from sentinelrx.note_ai import classify_note


ROOT = Path(__file__).resolve().parents[1]
STANDARD_RESULTS = ROOT / "benchmark_results.json"
ROBUST_RESULTS = ROOT / "robust_benchmark_results.json"
DEMO_BUNDLE = ROOT / "examples" / "demo_bundle.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def metric_card(label: str, value: str, help_text: str | None = None):
    st.metric(label, value, help=help_text)


def status_label(finding):
    return "EVIDENCE-CHECKED" if finding.verification_status == VerificationStatus.VERIFIED else "ABSTAIN"


def evidence_table(findings):
    rows = []
    for finding in findings:
        for ev in finding.evidence:
            rows.append({
                "Finding": finding.summary,
                "Status": status_label(finding),
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

st.info("AI reads the note. Rules check the records. The reviewer decides.")

bundle = load_json(DEMO_BUNDLE)
scenario = st.selectbox("Demo evidence", ["Complete synthetic transition", "Missing medication identity"])
if scenario == "Missing medication identity":
    for entry in bundle["entry"]:
        resource = entry.get("resource", {})
        if resource.get("id") == "discharge-lisinopril":
            resource.pop("medicationCodeableConcept", None)
st.caption("EVIDENCE-CHECKED = bundle-local predicate and source checks passed; not clinical correctness. Absence assumes complete supplied lists. Missing dose text is not assessed.")
result = analyze_bundle(bundle)

tabs = st.tabs([
    "Safety Review",
    "AI Note Review",
    "Medication Timeline",
    "Evidence Provenance",
    "Counterfactual Lab",
    "Evaluation",
])

with tabs[0]:
    st.subheader("Discharge Safety Review")
    verified = [f for f in result.findings if f.verification_status == VerificationStatus.VERIFIED]
    abstained = [f for f in result.findings if f.verification_status == VerificationStatus.ABSTAIN]

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Evidence-checked findings", str(len(verified)))
    with c2:
        metric_card("Abstentions", str(len(abstained)))
    with c3:
        metric_card("FHIR resources reviewed", str(len(result.medications)))

    if not result.findings:
        st.info("No supported discrepancies detected. Unassessed data and clinical intent still require review.")
    else:
        for finding in result.findings:
            status = status_label(finding)
            with st.expander(f"{status} · {finding.summary}", expanded=True):
                st.write(finding.rationale)
                st.caption(finding.verification_reason)
                st.caption(f"Finding type: {finding.finding_type.value}")
                st.write("Evidence")
                for ev in finding.evidence:
                    st.code(f"{ev.resource_type}/{ev.resource_id}  ·  {ev.role}")

with tabs[1]:
    st.subheader("AI-assisted note review")
    st.write("Select a medication, paste one synthetic transition note, then inspect the model's proposal alongside the original record evidence.")
    st.caption("Local TF-IDF + logistic regression, trained on 48 authored examples. No API key or external service. This is a small research classifier, not a clinical language model.")
    options = {m.medication_key: m.medication_display for m in result.medications if m.medication_key != "unknown"}
    key = st.selectbox("Medication to review (linked by you)", list(options), index=next((i for i, k in enumerate(options) if options[k] == "Metformin"), 0), format_func=lambda k: options[k])
    example = st.selectbox("Synthetic note scenario", ["Documented stop", "Documented continuation", "Ambiguous instruction", "Custom note"])
    examples = {"Documented stop": "The discharge plan says to discontinue this medication.",
                "Documented continuation": "Continue the home medication without changes.",
                "Ambiguous instruction": "It is unclear whether to stop or continue this medication.",
                "Custom note": ""}
    note = st.text_area("Original synthetic note", value=examples[example], max_chars=2000, key="note_"+example)
    if note.strip():
        proposal = classify_note(note)
        left, right = st.columns(2)
        with left:
            st.markdown("**Learned proposal - unconfirmed**")
            st.write(proposal.proposal.upper())
            st.caption(f"Model score {proposal.score:.2f}; top-two margin {proposal.margin:.2f}. Not calibrated confidence.")
            st.info(proposal.review_question)
            st.caption(proposal.reason)
            st.markdown("**Exact source text**")
            st.code(proposal.source_quote)
        with right:
            st.markdown("**Record evidence stays visible**")
            for finding in result.findings:
                if finding.medication_key == key:
                    st.write(f"{status_label(finding)} · {finding.summary}")
                    st.caption(finding.verification_reason)
            st.warning("A note proposal never removes a discrepancy or upgrades its evidence status. You supplied the medication link; the model has not verified it.")
        decision = st.selectbox("Reviewer annotation (demo only)", ["Unreviewed", "Needs source clarification", "Possible intended transition - requires confirmation", "Record discrepancy needs follow-up"])
        report = {"scope": "Synthetic demonstration; not a treatment decision", "medication_key": key,
                  "human_supplied_medication_link": True, "note_proposal": proposal.model_dump(),
                  "reviewer_annotation": decision,
                  "record_findings": [f.model_dump(mode="json") for f in result.findings if f.medication_key == key]}
        st.download_button("Download review audit JSON", json.dumps(report, indent=2), "sentinelrx-review.json", "application/json")

with tabs[2]:
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

with tabs[3]:
    st.subheader("Evidence Provenance")
    st.write("Evidence-checked findings resolve to source resources. Abstentions may identify missing or unresolvable evidence.")
    ev = evidence_table(result.findings)
    if ev.empty:
        st.info("No evidence links to show.")
    else:
        st.dataframe(ev, width="stretch", hide_index=True)
        st.caption("Checks establish bundle-local predicates, not clinical correctness or source completeness.")

with tabs[4]:
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
            st.write(f"• {status_label(f)} · {f.summary}")
    with right:
        st.markdown("**After**")
        if mutated_result.findings:
            for f in mutated_result.findings:
                st.write(f"• {status_label(f)} · {f.summary}")
        else:
            st.success("No remaining discrepancies in this scenario.")

    before_ids = {f.finding_id for f in result.findings if f.verification_status == VerificationStatus.VERIFIED}
    after_ids = {f.finding_id for f in mutated_result.findings}
    st.caption("Disappearing candidates are not proof of clinical resolution; check any abstentions above.")
    resolved = sorted(before_ids - after_ids)
    if resolved:
        st.success("Resolved by changed evidence: " + ", ".join(resolved))

with tabs[5]:
    st.subheader("Reproducible Evaluation")
    ai_path = ROOT / "note_ai_results.json"
    if ai_path.exists():
        ai = load_json(ai_path)
        st.write("Local learned note classifier: authored evaluation split")
        st.json({k: ai[k] for k in ["training_examples", "cases", "coverage", "accepted_accuracy", "overall_exact_accuracy", "unsafe_acceptances_on_abstain_cases"]})
        st.caption(ai["scope"] + " Scores are not calibrated clinical confidence.")
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

    challenge_path = ROOT / "perturbation_results.json"
    if challenge_path.exists():
        challenge = load_json(challenge_path)
        st.write("Authored development perturbations (not held-out)")
        st.json({k: v for k, v in challenge.items() if k != "rows"})

    st.warning(
        "These results measure deterministic behavior on generated synthetic test conditions. "
        "They are not clinical validation and should not be interpreted as real-world clinical performance."
    )

st.divider()
st.caption("Synthetic data only · Clinical decision support prototype · No autonomous diagnosis or prescribing")
