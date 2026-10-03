from sentinelrx.benchmark import build_cases, run_benchmark

def test_builds_requested_case_count():
    assert len(build_cases(120)) == 120

def test_benchmark_expected_structure():
    r = run_benchmark(120)
    assert r["sentinelrx"]["cases"] == 120
    assert r["naive_baseline"]["cases"] == 120

def test_sentinelrx_beats_naive_baseline_on_f1():
    r = run_benchmark(120)
    assert r["sentinelrx"]["f1"] > r["naive_baseline"]["f1"]

def test_sentinelrx_is_exact_on_generated_suite():
    r = run_benchmark(120)
    assert r["sentinelrx"]["exact_case_accuracy"] == 1.0
