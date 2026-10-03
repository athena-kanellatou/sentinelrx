from sentinelrx.robust_benchmark import build_robust_cases, run_robust_benchmark

def test_robust_suite_size():
    assert len(build_robust_cases()) == 90

def test_no_crashes_on_robust_suite():
    assert run_robust_benchmark()["crashes"] == 0

def test_verified_exact_accuracy():
    assert run_robust_benchmark()["verified_exact_accuracy"] == 1.0

def test_abstention_behavior_accuracy():
    assert run_robust_benchmark()["abstention_behavior_accuracy"] == 1.0
