from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.filter import segment_text
from app.model_builder import build_domain_model
from app.file_processor import extract_text_from_file

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
    """Process requirements from a file (PDF, DOCX, or TXT)"""
    try:
        text = extract_text_from_file(path)
        segments = segment_text(text, doc_id=doc_id)
        model = build_domain_model(doc_id, segments)

        return {
            "file_path": path,
            "file_type": Path(path).suffix,
            "extracted_length": len(text),
            "model": model
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
