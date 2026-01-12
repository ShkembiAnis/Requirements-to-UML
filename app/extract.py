from __future__ import annotations

import re
from typing import List, Dict, Set

from app.filter import Segment


# Very small stopword list just to reduce noise
_STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "by",
    "is", "are", "be", "as", "at", "from", "this", "that", "these", "those",
    "system", "shall", "must", "should", "can", "may", "will", "req", "fr",
    "nfr", "us", "info", "def", "con", "shall", "must", "should",
    "project", "document", "scope", "stakeholders", "each", "person", "name",
    "def", "con", "req"
}


def _ok_concept(token: str) -> bool:
    low = token.lower()
    if low in _STOPWORDS:
        return False
    if re.fullmatch(r"\d+", token):
        return False
    if re.fullmatch(r"(req|fr|nfr|us)\s*[-:]?\s*\d+", low):
        return False
    if re.fullmatch(r"[a-z]+-\d+", low):
        return False
    if re.fullmatch(r"[a-z]+[A-Z][A-Za-z0-9_]*", token):
        return False
    if token.lower().endswith("id"):
        return False
    return True


def extract_candidate_classes(segments: List[Segment]) -> Dict[str, Set[str]]:
    """
    Heuristic: capitalized terms + nouns after 'a/an/the'
    """
    classes: Dict[str, Set[str]] = {}

    for s in segments:
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", s.text)

        # Capitalized words (likely domain concepts)
        capitalized = [
            t for t in tokens
            if t[0].isupper() and _ok_concept(t)
        ]

        # Lowercase nouns after articles: "a customer", "the order"
        lower = s.text.lower()
        after_articles = [
            w.capitalize()
            for _, w in re.findall(r"\b(a|an|the|one)\s+([a-z][a-z0-9_-]*)", lower)
            if _ok_concept(w)
        ]

        for c in set(capitalized + after_articles):
            classes.setdefault(c, set()).add(s.segment_id)

    return classes


def extract_attributes(segments: List[Segment]) -> Dict[str, List[Dict]]:
    """
    Extract attributes from simple definition patterns:
    - 'DEF A customer ... has a customerId and a name.'
    - 'A Customer ... has customerId and name.'
    """
    attrs: Dict[str, List[Dict]] = {}

    for s in segments:
        txt = s.text.strip()

        # Remove leading labels like "DEF ", "REQ-1 ", "CON "
        txt_clean = re.sub(r"^\s*(DEF|CON|INFO)\s+", "", txt, flags=re.IGNORECASE)
        txt_clean = re.sub(r"^\s*(REQ|FR|NFR|US)\s*[-:]?\s*\d+\s+", "", txt_clean, flags=re.IGNORECASE)

        # Pattern: "A customer ... has customerId and name"
        m = re.search(r"\b(a|an|the)\s+([a-z][a-z0-9_-]*)\b.*\b(has|have|contains|includes)\b\s+(.*)", txt_clean, flags=re.IGNORECASE)
        if not m:
            continue

        cls = m.group(2).capitalize()
        tail = m.group(4)

        parts = re.split(r",|\band\b", tail)
        for p in parts:
            nm = re.search(r"\b(?!a\b|an\b|the\b)([a-z][A-Za-z0-9_]*)\b", p.strip(), flags=re.IGNORECASE)
            if not nm:
                continue
            attr_name = nm.group(1)
            attrs.setdefault(cls, []).append({
                "name": attr_name,
                "type": "string",
                "source_segments": [s.segment_id]
            })

    return attrs


def extract_relations(segments: List[Segment], class_names: Set[str]) -> List[Dict]:
    verbs = [
        "place", "places",
        "contain", "contains",
        "reference", "references",
        "include", "includes"
    ]
    verb_pattern = r"(" + "|".join(map(re.escape, verbs)) + r")"

    # Also consider lowercase versions of class names
    class_variants = {}
    for cn in class_names:
        class_variants[cn] = [cn, cn.lower()]

    rels: List[Dict] = []
    for s in segments:
        txt = s.text

        # Remove leading REQ-1 etc
        txt_clean = re.sub(r"^\s*(REQ|FR|NFR|US)\s*[-:]?\s*\d+\s+", "", txt, flags=re.IGNORECASE)

        for a in class_names:
            for b in class_names:
                if a == b:
                    continue

                a_vars = class_variants[a]
                b_vars = class_variants[b]

                # Try patterns like:
                # "customer ... place an order"
                for av in a_vars:
                    for bv in b_vars:
                        pattern = (rf"\b{re.escape(av)}\b(?:\W+\w+){{0,6}}\W+"
                                   rf"{verb_pattern}\W+(?:\w+\W+){{0,6}}\b{re.escape(bv)}\b")
                        if re.search(pattern, txt_clean, flags=re.IGNORECASE):
                            rels.append({
                                "source": a,
                                "target": b,
                                "label": "association",
                                "type": "association",
                                "cardinality": {"source": "1", "target": "0..*"},
                                "source_segments": [s.segment_id]
                            })

    # Deduplicate (source,target)
    seen = set()
    unique = []
    for r in rels:
        key = (r["source"], r["target"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique
