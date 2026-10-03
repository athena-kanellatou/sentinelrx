from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from sentinelrx.engine import analyze_bundle
from sentinelrx.models import AnalysisResult

app = FastAPI(
    title="SentinelRx API",
    version="0.4.0",
    description="Evidence-grounded medication-transition review for synthetic FHIR R4 bundles.",
)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalysisResult)
def analyze(bundle: dict[str, Any]) -> AnalysisResult:
    try:
        return analyze_bundle(bundle)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
