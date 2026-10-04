from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from sentinelrx.engine import analyze_bundle
from sentinelrx.models import AnalysisResult
from sentinelrx.note_ai import NoteProposal, classify_note

MAX_BODY_BYTES = 1_000_000
app = FastAPI(title="SentinelRx API", version="0.5.0",
              description="Synthetic medication review and local learned note triage. Not clinical validation.")


@app.middleware("http")
async def bound_request_body(request: Request, call_next):
    # Count actual streamed bytes; do not trust Content-Length.
    from starlette.responses import JSONResponse
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_BODY_BYTES:
            return JSONResponse(status_code=413, content={"detail": "Request exceeds 1 MB limit."})
    request._body = bytes(body)
    return await call_next(request)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResult)
def analyze(bundle: dict) -> AnalysisResult:
    try:
        return analyze_bundle(bundle)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class NoteRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


@app.post("/note-review", response_model=NoteProposal)
def note_review(note: NoteRequest) -> NoteProposal:
    try:
        return classify_note(note.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
