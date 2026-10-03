from pathlib import Path
import json

from sentinelrx.engine import analyze_bundle
from sentinelrx.models import FindingType, VerificationStatus

ROOT = Path(__file__).resolve().parents[1]

def test_demo_script_exists():
    assert (ROOT / "DEMO_SCRIPT.md").exists()

def test_gallery_checklist_exists():
    assert (ROOT / "DEVPOST_GALLERY.md").exists()

def test_benchmark_files_exist():
    assert (ROOT / "benchmark_results.json").exists()
    assert (ROOT / "robust_benchmark_results.json").exists()

def test_demo_bundle_is_valid_json():
    json.loads((ROOT / "examples" / "demo_bundle.json").read_text())

def test_demo_bundle_produces_expected_findings():
    bundle = json.loads((ROOT / "examples" / "demo_bundle.json").read_text())
    result = analyze_bundle(bundle)

    verified = [f for f in result.findings if f.verification_status == VerificationStatus.VERIFIED]
    assert len(verified) == 3
    assert {f.finding_type for f in verified} == {
        FindingType.OMISSION,
        FindingType.DUPLICATION,
        FindingType.DOSE_CHANGE,
    }
