"""Local learned note triage. It cannot mutate records, findings or review decisions."""
from functools import lru_cache
from hashlib import sha256
from importlib.resources import files
import json
import re

from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

MODEL_VERSION = "note-triage-1"
MIN_SCORE = 0.50
MIN_MARGIN = 0.15


class NoteProposal(BaseModel):
    model_version: str = MODEL_VERSION
    training_sha256: str
    source_sha256: str
    source_quote: str
    proposal: str
    disposition: str  # proposed / abstain; never evidence-checked
    score: float = Field(ge=0, le=1)
    margin: float = Field(ge=0, le=1)
    reason: str
    review_question: str


@lru_cache(maxsize=1)
def trained_model():
    data = files("sentinelrx").joinpath("data/note_train.json").read_bytes()
    rows = json.loads(data)
    texts, labels = [], []
    for label, examples in rows.items():
        texts.extend(examples)
        labels.extend([label] * len(examples))
    model = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), lowercase=True),
        LogisticRegression(C=8.0, max_iter=1000, random_state=0),
    )
    model.fit(texts, labels)
    return model, sha256(data).hexdigest()


QUESTIONS = {
    "stop": "Does this note document an intended stop, and does it apply to the selected medication and transition?",
    "continue": "Does the discharge list preserve the continuation described in this note?",
    "change": "Does the recorded dose or schedule agree with the documented change?",
    "start": "Is the new discharge entry consistent with the start described in this note?",
}


def classify_note(text: str) -> NoteProposal:
    if not isinstance(text, str) or not text.strip() or len(text) > 2000:
        raise ValueError("Provide one non-empty synthetic medication note, at most 2000 characters.")
    model, training_hash = trained_model()
    probabilities = model.predict_proba([text])[0]
    ranked = probabilities.argsort()
    label = str(model.classes_[ranked[-1]])
    score = float(probabilities[ranked[-1]])
    margin = score - float(probabilities[ranked[-2]])
    # Scope guards deliberately override a learned score. This is not full negation NLP.
    uncertain = re.search(r"\b(unclear|whether|consider|might|maybe|possibly|if|unless|or|not|never|no)\b|\?", text, re.I)
    mixed = re.search(r"\b(and|but|however)\b", text, re.I)
    supported = score >= MIN_SCORE and margin >= MIN_MARGIN and not uncertain and not mixed
    reason = ("Learned text classification; source linkage and clinical intent require human confirmation."
              if supported else "Low model separation or unsupported negation, conditional, question or compound statement.")
    return NoteProposal(
        training_sha256=training_hash, source_sha256=sha256(text.encode()).hexdigest(),
        source_quote=text, proposal=label if supported else "abstain",
        disposition="proposed" if supported else "abstain", score=score, margin=margin,
        reason=reason, review_question=QUESTIONS[label] if supported else "Read the original note and clarify the intended transition with its author.",
    )
