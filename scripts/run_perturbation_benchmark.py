import json
from pathlib import Path
from sentinelrx.perturbation import run_challenges
result = run_challenges()
Path('perturbation_results.json').write_text(json.dumps(result, indent=2))
print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))
