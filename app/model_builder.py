from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Set

from app.filter import Segment, filter_relevant_segments, quality_metrics
from app.extract import extract_candidate_classes, extract_attributes, extract_relations


def build_domain_model(doc_id: str, all_segments: List[Segment]) -> Dict:
    kept = filter_relevant_segments(all_segments)
    q = quality_metrics(all_segments, kept)

    class_map = extract_candidate_classes(kept)  # class -> set(segment_id)
    class_names: Set[str] = set(class_map.keys())

    attrs_map = extract_attributes(kept)
    relations = extract_relations(kept, class_names)

    classes: List[Dict] = []
    for cls_name in sorted(class_names):
        classes.append({
            "name": cls_name,
            "attributes": attrs_map.get(cls_name, []),
            "source_segments": sorted(list(class_map.get(cls_name, set())))
        })

    model = {
        "metadata": {
            "doc_id": doc_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "0.1"
        },
        "segments": [
            {
                "segment_id": s.segment_id,
                "label": s.label,
                "text": s.text,
                "source": {"page": s.page, "section": s.section}
            }
            for s in all_segments
        ],
        "classes": classes,
        "relations": relations,
        "quality": {
            **q,
            "num_classes": len(classes),
            "num_relations": len(relations)
        }
    }
    return model
