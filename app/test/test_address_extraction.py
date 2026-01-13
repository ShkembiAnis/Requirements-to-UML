# Quick test script: test_address_extraction.py
from app.filter import segment_text

text = "DEF An Address contains street, city, state, postalCode, and country."
segments = segment_text(text)

print("Segments:")
for s in segments:
    print(f"  {s.segment_id}: {s.label} - {s.text}")

from app.extract import extract_candidate_classes, extract_attributes

classes = extract_candidate_classes(segments)
print(f"\nExtracted classes: {classes}")

attrs = extract_attributes(segments)
print(f"\nExtracted attributes: {attrs}")
