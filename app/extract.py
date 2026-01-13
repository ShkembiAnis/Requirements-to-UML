from __future__ import annotations

import re
from typing import List, Dict, Set

from app.filter import Segment


# Expanded stopword list
_STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "by",
    "is", "are", "be", "as", "at", "from", "this", "that", "these", "those",
    "system", "shall", "must", "should", "can", "may", "will", "req", "fr",
    "nfr", "us", "info", "def", "con", "shall", "must", "should",
    "project", "document", "scope", "stakeholders", "each", "person",
    "def", "con", "req", "one", "more", "exactly", "zero", "all",
    "within", "between", "greater", "less", "than", "equal", "not",
    "i", "we", "you", "they", "it", "he", "she",
    "commerce", "management", "specification", "version",
    "introduction", "purpose", "functional", "non-functional",
    "registered", "temporary", "financial", "item", "purchase"
}

# Common attribute keywords (NOT classes)
_ATTRIBUTE_KEYWORDS = {
    "id", "name", "email", "password", "address", "phone", "date", "time",
    "amount", "price", "quantity", "status", "description", "type", "code",
    "number", "value", "flag", "url", "path", "key", "token", "timestamp",
    "created", "updated", "modified", "deleted", "active", "enabled",
    "firstname", "lastname", "username", "fullname", "displayname",
    "street", "city", "state", "country", "zipcode", "postalcode",
    "total", "subtotal", "discount", "tax", "shipping", "rating", "comment",
    "proof", "stock", "unit", "transaction"
}


def _normalize_class_name(name: str) -> str:
    """Normalize class name to handle case variations"""
    # Convert to title case for consistency
    # "orderitem" → "OrderItem"
    # Handle camelCase: "OrderItem" stays "OrderItem"

    # If already camelCase, keep it
    if re.match(r'^[A-Z][a-z]+[A-Z]', name):
        return name

    # Otherwise, just capitalize first letter
    return name.capitalize()


def _is_likely_attribute(token: str) -> bool:
    """Check if a token is likely an attribute rather than a class"""
    low = token.lower()

    # Check if it's a known attribute keyword
    if low in _ATTRIBUTE_KEYWORDS:
        return True

    # Check if it ends with common attribute suffixes
    attribute_suffixes = ["id", "name", "date", "time", "amount", "price",
                          "count", "number", "code", "status", "type", "quantity"]
    if any(low.endswith(suffix) for suffix in attribute_suffixes):
        return True

    # Check for camelCase attributes starting with lowercase
    if re.match(r'^[a-z]+[A-Z][a-zA-Z]*$', token):
        return True

    return False


def _ok_concept(token: str) -> bool:
    """Check if token is a valid class concept"""
    low = token.lower()

    # Special case: "Address" (capitalized) is a valid class
    if token == "Address":
        return True

    # Too short
    if len(token) < 3:
        return False

    if low in _STOPWORDS:
        return False

    if re.fullmatch(r"\d+", token):
        return False

    if re.fullmatch(r"(req|fr|nfr|us)\s*[-:]?\s*\d+", low):
        return False

    if re.fullmatch(r"[a-z]+-\d+", low):
        return False

    # Reject common non-domain words
    if low in ["email", "price", "quantity", "rating", "proof", "zero", "stock"]:
        return False

    # Don't consider it a class if it's likely an attribute
    if _is_likely_attribute(token):
        return False

    return True


def extract_candidate_classes(segments: List[Segment]) -> Dict[str, Set[str]]:
    """Extract candidate class names from segments"""
    classes: Dict[str, Set[str]] = {}

    for s in segments:
        if s.label == "INFO":
            continue

        if s.label == "DEF":
            # Pattern: "DEF A/An/The ClassName ..."
            # Don't use IGNORECASE for the class name part
            def_match = re.search(
                r'DEF\s+(?:A|An|The)\s+([A-Z][a-zA-Z]+)',
                s.text  # Remove IGNORECASE flag
            )
            if def_match:
                class_name = _normalize_class_name(def_match.group(1))
                if _ok_concept(class_name):
                    classes.setdefault(class_name, set()).add(s.segment_id)
                    continue

        # For REQ/CON statements
        if s.label in ["REQ", "CON"]:
            entity_matches = re.findall(
                r'\b(?:a|an|the|each|every)\s+([a-z][a-z]+(?:[A-Z][a-z]+)?)\b',
                s.text
            )
            for entity in entity_matches:
                class_name = _normalize_class_name(entity)
                if _ok_concept(class_name) and len(entity) > 3:
                    classes.setdefault(class_name, set()).add(s.segment_id)

    return classes


def extract_attributes(segments: List[Segment]) -> Dict[str, List[Dict]]:
    """
    Extract attributes from DEF statements primarily
    """
    attrs: Dict[str, List[Dict]] = {}

    for s in segments:
        # Focus on DEF segments
        if s.label != "DEF":
            continue

        txt = s.text.strip()

        # Remove "DEF " prefix
        txt_clean = re.sub(r"^\s*DEF\s+", "", txt, flags=re.IGNORECASE)

        # Pattern 1: "A Customer is ... with/has customerId, emailAddress, and fullName"
        match1 = re.search(
            r'(?:A|An|The)\s+([A-Z][a-zA-Z]+)\s+.*?\b(?:with|has|contains?|includes?)\s+(?:a|an)?\s*(.*?)(?:\.|$)',
            txt_clean,
            flags=re.IGNORECASE
        )

        if match1:
            class_name = _normalize_class_name(match1.group(1))
            attributes_text = match1.group(2)

            if _ok_concept(class_name):
                attrs.setdefault(class_name, [])
                _extract_attribute_names(attributes_text, class_name, s.segment_id, attrs)
                continue

        # Pattern 2: "A Payment ... includes paymentId, paymentMethod, paymentDate, amount, and transactionStatus"
        match2 = re.search(
            r'(?:A|An|The)\s+([A-Z][a-zA-Z]+)\s+.*?(?:with|has|includes?|contains?)\s+([\w,\s]+)',
            txt_clean,
            flags=re.IGNORECASE
        )

        if match2:
            class_name = _normalize_class_name(match2.group(1))
            attributes_text = match2.group(2)

            if _ok_concept(class_name):
                attrs.setdefault(class_name, [])
                # Split by period to avoid grabbing next sentence
                attributes_text = attributes_text.split('.')[0]
                _extract_attribute_names(attributes_text, class_name, s.segment_id, attrs)

    return attrs


def _extract_attribute_names(text: str, class_name: str, segment_id: str, attrs: Dict):
    """Helper to extract attribute names from text"""
    # Split by 'and' and commas
    parts = re.split(r',|\band\b', text)

    for p in parts:
        p = p.strip()

        # Remove leading articles and prepositions
        p = re.sub(r'^\s*(?:a|an|the|with|for|of)\s+', '', p, flags=re.IGNORECASE)

        # Extract attribute name (camelCase or single word)
        # Match: "customerId" or "emailAddress" or "fullName"
        match = re.search(r'\b([a-z][a-zA-Z0-9_]*)\b', p)
        if not match:
            continue

        attr_name = match.group(1)

        # Skip if it's a stopword or non-attribute word
        if attr_name.lower() in _STOPWORDS or attr_name.lower() in ["user", "person", "item", "thing", "object", "has", "includes", "contains", "with"]:
            continue

        # Skip very short attributes
        if len(attr_name) < 3:
            continue

        # Try to infer data type
        data_type = _infer_data_type(attr_name, p)

        # Check if attribute already exists
        existing = [a for a in attrs[class_name] if a['name'].lower() == attr_name.lower()]
        if not existing:
            attrs[class_name].append({
                "name": attr_name,
                "type": data_type,
                "source_segments": [segment_id]
            })


def _infer_data_type(attr_name: str, context: str) -> str:
    """Infer data type from attribute name and context"""
    attr_lower = attr_name.lower()
    context_lower = context.lower()

    # ID fields
    if attr_lower.endswith('id'):
        return "int"

    # Date/time fields
    if any(x in attr_lower for x in ['date', 'time', 'timestamp']):
        return "Date"

    # Numeric fields
    if any(x in attr_lower for x in ['amount', 'price', 'cost', 'total', 'subtotal']):
        return "decimal"

    if any(x in attr_lower for x in ['quantity', 'count', 'number', 'rating']):
        return "int"

    # Boolean fields
    if any(x in attr_lower for x in ['is', 'has', 'enabled', 'active']):
        return "boolean"

    # Specific types
    if 'email' in attr_lower:
        return "String"

    if 'password' in attr_lower:
        return "String"

    if 'address' in attr_lower or 'street' in attr_lower or 'city' in attr_lower:
        return "String"

    if 'phone' in attr_lower:
        return "String"

    # Default
    return "String"


def extract_relations(segments: List[Segment], class_names: Set[str]) -> List[Dict]:
    """Extract relationships between classes"""

    # Create all possible variants
    compound_variants = {}
    for name in class_names:
        compound_variants[name.lower()] = name
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', name).lower()
        compound_variants[spaced] = name
        compound_variants[name.lower() + "s"] = name
        compound_variants[spaced + "s"] = name
        compound_variants[name.lower() + "es"] = name

    verbs = [
        "place", "places", "contain", "contains", "reference", "references",
        "include", "includes", "have", "has", "create", "creates",
        "write", "writes", "add", "adds", "save", "saves",
        "deliver", "delivers", "delivered", "send", "sends"
    ]

    rels: List[Dict] = []

    for s in segments:
        if s.label == "INFO":
            continue

        txt_lower = s.text.lower()
        txt_clean = re.sub(r"^\s*(req|fr|nfr|us|def)\s*[-:]?\s*\d+\s+", "", txt_lower)

        found_in_segment = set()

        # ====================================================================
        # Pattern 1: "must/shall verb"
        # ====================================================================
        must_pattern = r'(?:each|every|a|an|the)\s+([\w\s]+?)\s+(?:must|shall)\s+(\w+)\s+.*?\b([\w\s]+?)(?:\s+(?:and|or|to|for|with)|\.|,|$)'

        for match in re.finditer(must_pattern, txt_clean):
            source_raw = match.group(1).strip()
            verb = match.group(2)
            target_raw = match.group(3).strip()
            target_raw = re.sub(r'^(a|an|the|one|more|exactly|zero|multiple)\s+', '', target_raw).strip()

            source_name = compound_variants.get(source_raw)
            target_name = compound_variants.get(target_raw)

            if source_name and target_name and source_name != target_name:
                rel_key = (source_name, target_name, verb)
                if rel_key not in found_in_segment:
                    found_in_segment.add(rel_key)
                    rels.append({
                        "source": source_name,
                        "target": target_name,
                        "label": verb,
                        "type": "association",
                        "cardinality": _infer_cardinality(match.group(0)),
                        "source_segments": [s.segment_id]
                    })

        # ====================================================================
        # Pattern 2: Direct verb relationships
        # ====================================================================
        for source_variant, source_name in compound_variants.items():
            for target_variant, target_name in compound_variants.items():
                if source_name == target_name:
                    continue

                for verb in verbs:
                    pattern = rf"\b{re.escape(source_variant)}\b(?:\W+\w+){{0,8}}\W+{re.escape(verb)}\W+(?:\w+\W+){{0,6}}\b{re.escape(target_variant)}\b"

                    if re.search(pattern, txt_clean):
                        rel_key = (source_name, target_name, verb)
                        if rel_key not in found_in_segment:
                            found_in_segment.add(rel_key)
                            rels.append({
                                "source": source_name,
                                "target": target_name,
                                "label": verb,
                                "type": "association",
                                "cardinality": _infer_cardinality(txt_clean),
                                "source_segments": [s.segment_id]
                            })
                        break

        # ====================================================================
        # Pattern 3: "shall be able to save ... addresses"
        # FIX: Extract source and verb, then search for target class in sentence
        # ====================================================================
        able_pattern = r'(?:a|an|the)\s+([\w]+)\s+shall be able to\s+([\w]+)'

        for match in re.finditer(able_pattern, txt_clean):
            source_raw = match.group(1).strip()
            verb = match.group(2).strip()

            source_name = compound_variants.get(source_raw)

            if source_name:
                # Now look for any known class name in the rest of the sentence
                # Search after the verb
                rest_of_sentence = txt_clean[match.end():]

                target_name = None
                for class_variant, class_name in compound_variants.items():
                    if class_variant in rest_of_sentence and class_name != source_name:
                        target_name = class_name
                        break

                if target_name:
                    rel_key = (source_name, target_name, verb)
                    if rel_key not in found_in_segment:
                        found_in_segment.add(rel_key)
                        rels.append({
                            "source": source_name,
                            "target": target_name,
                            "label": verb,
                            "type": "association",
                            "cardinality": _infer_cardinality(txt_clean),
                            "source_segments": [s.segment_id]
                        })

        # ====================================================================
        # Pattern 4: "must be delivered to ... address"
        # FIX: Extract source and verb, then search for target class
        # ====================================================================
        passive_pattern = r'(?:each|every|a|an|the)\s+([\w]+)\s+must be\s+([\w]+)\s+to'

        for match in re.finditer(passive_pattern, txt_clean):
            source_raw = match.group(1).strip()
            verb = match.group(2).strip()

            source_name = compound_variants.get(source_raw)

            if source_name:
                # Look for target class after "to"
                rest_of_sentence = txt_clean[match.end():]

                target_name = None
                for class_variant, class_name in compound_variants.items():
                    if class_variant in rest_of_sentence and class_name != source_name:
                        target_name = class_name
                        break

                if target_name:
                    rel_key = (source_name, target_name, verb)
                    if rel_key not in found_in_segment:
                        found_in_segment.add(rel_key)
                        rels.append({
                            "source": source_name,
                            "target": target_name,
                            "label": verb,
                            "type": "association",
                            "cardinality": _infer_cardinality(txt_clean),
                            "source_segments": [s.segment_id]
                        })

    # Global deduplication
    seen_pairs = set()
    unique = []

    for r in rels:
        pair = tuple(sorted([r["source"], r["target"]]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique.append(r)

    return unique


def _infer_cardinality(text: str) -> Dict[str, str]:
    """Infer cardinality from text"""
    text_lower = text.lower()

    # Check for specific cardinality mentions
    if "exactly one" in text_lower:
        return {"source": "1", "target": "1"}

    if "one or more" in text_lower:
        return {"source": "1", "target": "1..*"}

    if "zero or more" in text_lower:
        return {"source": "1", "target": "0..*"}

    if "multiple" in text_lower or "many" in text_lower:
        return {"source": "1", "target": "0..*"}

    # Default
    return {"source": "1", "target": "0..*"}
