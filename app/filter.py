from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Dict


LABEL_REQ = "REQ"
LABEL_DEF = "DEF"
LABEL_CON = "CON"
LABEL_INFO = "INFO"


@dataclass
class Segment:
    segment_id: str
    label: str
    text: str
    page: int = 0
    section: str = ""


_REQ_PATTERNS = [
    r"\bshall\b",
    r"\bmust\b",
    r"\bshould\b",
    r"\bis required to\b",
    r"\brequires\b",
    r"\bhas to\b",
]
_DEF_PATTERNS = [
    r"^def\b",
    r"^definition\b",
    r"\bis defined as\b",
    r"\bmeans\b",
    r"^glossary\b",
]
_CON_PATTERNS = [
    r"\bunique\b",
    r"\bwithin\b.*\bseconds\b",
    r"\bnot exceed\b",
    r"\bmaximum\b",
    r"\bminimum\b",
    r"\bvalidation\b",
    r"\bconstraint\b",
    r"\bencrypted\b",
    r"\bgdpr\b",
]


_REQ_ID_PATTERN = re.compile(r"^\s*(REQ|FR|NFR|US)\s*[-:]?\s*\d+", re.IGNORECASE)


def _matches_any(text: str, patterns: List[str]) -> bool:
    t = text.strip().lower()
    return any(re.search(p, t, flags=re.IGNORECASE) for p in patterns)


def label_sentence(text: str) -> str:
    """
    Labels a sentence/paragraph as REQ/DEF/CON/INFO using simple rules.
    This is your week-1 baseline; you can replace it with a classifier later.
    """
    t = text.strip()
    if not t:
        return LABEL_INFO

    # Heuristic: explicit requirement IDs
    if _REQ_ID_PATTERN.search(t):
        return LABEL_REQ

    # Definitions often start with DEF/Definition/Glossary
    if _matches_any(t, _DEF_PATTERNS):
        return LABEL_DEF

    # Constraints are "rules" often containing unique, max/min, performance limits
    if _matches_any(t, _CON_PATTERNS):
        return LABEL_CON

    # Requirements often use shall/must/should...
    if _matches_any(t, _REQ_PATTERNS):
        return LABEL_REQ

    return LABEL_INFO


def split_into_candidates(raw_text: str) -> List[str]:
    """
    Splits raw text into candidate chunks. For week-1:
    - split by newline
    - keep non-empty lines
    """
    lines = [ln.strip() for ln in raw_text.splitlines()]
    return [ln for ln in lines if ln]


def segment_text(raw_text: str, doc_id: str = "doc") -> List[Segment]:
    candidates = split_into_candidates(raw_text)
    segments: List[Segment] = []
    for i, chunk in enumerate(candidates, start=1):
        seg_id = f"S{i}"
        label = label_sentence(chunk)
        segments.append(Segment(segment_id=seg_id, label=label, text=chunk))
    return segments


def filter_relevant_segments(segments: List[Segment]) -> List[Segment]:
    """
    Keep segments that are relevant for extraction.
    We keep REQ/DEF/CON; ignore INFO.
    """
    return [s for s in segments if s.label in (LABEL_REQ, LABEL_DEF, LABEL_CON)]


def quality_metrics(all_segments: List[Segment], kept: List[Segment]) -> Dict[str, float | int]:
    total = len(all_segments)
    kept_n = len(kept)
    ratio = (kept_n / total) if total else 0.0
    return {
        "num_segments": total,
        "kept_segments": kept_n,
        "filter_ratio": round(ratio, 4),
    }
