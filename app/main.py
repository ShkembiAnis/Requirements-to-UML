# app/main.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.filter import segment_text
from app.model_builder import build_domain_model
from app.miro_visualizer import visualize_domain_model


app = FastAPI(title="Requirements to UML Prototype", version="0.1")


class ProcessRequest(BaseModel):
    doc_id: str = Field(default="doc", description="Document identifier")
    text: str = Field(..., description="Plain text requirements content")


class VisualizeRequest(BaseModel):
    board_id: str = Field(..., description="Miro board ID")
    doc_id: str = Field(default="doc", description="Document identifier")
    text: str = Field(..., description="Plain text requirements content")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process")
def process(req: ProcessRequest):
    """Process requirements and return domain model JSON"""
    segments = segment_text(req.text, doc_id=req.doc_id)
    model = build_domain_model(req.doc_id, segments)
    return model


@app.post("/visualize")
def visualize(req: VisualizeRequest):
    """Process requirements and visualize in Miro"""
    # First, build the domain model
    segments = segment_text(req.text, doc_id=req.doc_id)
    model = build_domain_model(req.doc_id, segments)

    # Then visualize it in Miro
    visualization = visualize_domain_model(req.board_id, model)

    return {
        "domain_model": model,
        "visualization": visualization
    }


@app.post("/process-file")
def process_file(path: str, doc_id: str = "doc"):
    """Process requirements from a file"""
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    text = p.read_text(encoding="utf-8")
    segments = segment_text(text, doc_id=doc_id)
    model = build_domain_model(doc_id, segments)
    return model


@app.post("/visualize-file")
def visualize_file(board_id: str, path: str, doc_id: str = "doc"):
    """Process requirements from a file and visualize in Miro"""
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    text = p.read_text(encoding="utf-8")
    segments = segment_text(text, doc_id=doc_id)
    model = build_domain_model(doc_id, segments)

    visualization = visualize_domain_model(board_id, model)

    return {
        "domain_model": model,
        "visualization": visualization
    }
