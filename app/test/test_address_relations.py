# test_address_relations.py
from app.filter import segment_text
from app.extract import extract_candidate_classes, extract_relations

# Test the exact text from your PDF
text1 = "REQ-13 A customer shall be able to save multiple shipping addresses."
text2 = "REQ-14 Each order must be delivered to exactly one address."

print("Testing Address Relations Extraction")
print("=" * 60)

# Process both texts
all_text = f"{text1}\n{text2}"
segments = segment_text(all_text)

print("\nSegments:")
for s in segments:
    print(f"  {s.segment_id}: {s.label} - {s.text}")

# Extract classes (we need to know what classes exist)
classes = extract_candidate_classes(segments)
print(f"\nClasses: {set(classes.keys())}")

# Manually add the classes we expect for this test
test_classes = {"Customer", "Order", "Address"}
print(f"Using classes for relation extraction: {test_classes}")

# Extract relations
relations = extract_relations(segments, test_classes)

print(f"\n🔗 Relations extracted: {len(relations)}")
for rel in relations:
    print(f"  - {rel['source']} --{rel['label']}--> {rel['target']}")

if len(relations) == 0:
    print("\n❌ NO RELATIONS EXTRACTED!")
    print("This means the patterns aren't matching.")
else:
    print("\n✅ Relations successfully extracted!")
