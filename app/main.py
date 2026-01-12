from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.filter import segment_text
from app.model_builder import build_domain_model


app = FastAPI(title="Requirements to UML Prototype", version="0.1")


class ProcessRequest(BaseModel):
    doc_id: str = Field(default="doc", description="Document identifier")
    text: str = Field(..., description="Plain text requirements content")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process")
def process(req: ProcessRequest):
    segments = segment_text(req.text, doc_id=req.doc_id)
    model = build_domain_model(req.doc_id, segments)
    return model


@app.post("/process-file")
def process_file(path: str, doc_id: str = "doc"):
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    text = p.read_text(encoding="utf-8")
    segments = segment_text(text, doc_id=doc_id)
    model = build_domain_model(doc_id, segments)
    return model
