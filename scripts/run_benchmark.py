import json
from pathlib import Path
from sentinelrx.benchmark import run_benchmark

result = run_benchmark(120)
out = Path("benchmark_results.json")
out.write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
print(f"\nSaved to {out}")
