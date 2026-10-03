from pathlib import Path
import json

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
