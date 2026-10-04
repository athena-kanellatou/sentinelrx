"""One authored split, not external validation. No score target or threshold tuning."""
from hashlib import sha256
from importlib.resources import files
import json
from pathlib import Path
from sklearn.metrics import classification_report
from sentinelrx.note_ai import classify_note, MIN_SCORE, MIN_MARGIN, MODEL_VERSION

raw = files('sentinelrx').joinpath('data/note_eval.json').read_bytes()
rows = json.loads(raw)
results = []
for row in rows:
    p = classify_note(row['text'])
    results.append({**row, **p.model_dump(), 'correct': row['label'] == p.proposal})
accepted = [r for r in results if r['disposition'] == 'proposed']
report = {
    'scope': 'Author-written synthetic split, excluded from training; not independently authored, clinical, or external validation. Fixed thresholds, no tuning against this split.',
    'model_version': MODEL_VERSION,
    'training_sha256': results[0]['training_sha256'], 'evaluation_sha256': sha256(raw).hexdigest(),
    'minimum_score': MIN_SCORE, 'minimum_margin': MIN_MARGIN,
    'training_examples': 48, 'cases': len(rows),
    'coverage': len(accepted) / len(rows),
    'accepted_accuracy': sum(r['correct'] for r in accepted) / len(accepted) if accepted else None,
    'overall_exact_accuracy': sum(r['correct'] for r in results) / len(rows),
    'unsafe_acceptances_on_abstain_cases': sum(r['label'] == 'abstain' and r['disposition'] == 'proposed' for r in results),
    'majority_class_accuracy': max(sum(r['label']==label for r in rows) for label in {r['label'] for r in rows}) / len(rows),
    'classification_report': classification_report([r['label'] for r in results], [r['proposal'] for r in results], output_dict=True, zero_division=0),
    'rows': results,
}
Path('note_ai_results.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in {'rows','classification_report'}}, indent=2))
