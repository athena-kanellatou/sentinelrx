import json
from pathlib import Path
from sentinelrx.robust_benchmark import run_robust_benchmark
r=run_robust_benchmark()
Path("robust_benchmark_results.json").write_text(json.dumps(r, indent=2))
print(json.dumps({k:v for k,v in r.items() if k!="rows"}, indent=2))
