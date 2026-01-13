# test_full_pipeline.py
from pathlib import Path
from app.filter import segment_text
from app.model_builder import build_domain_model
from app.miro_visualizer import visualize_domain_model

BOARD_ID = "uXjVGRZh1IE="

# Load sample requirements
sample_path = Path("app/sample_requirements.txt")
text = sample_path.read_text()

print("=" * 60)
print("STEP 1: Processing requirements text...")
print("=" * 60)
segments = segment_text(text)
print(f"Found {len(segments)} segments")

print("\n" + "=" * 60)
print("STEP 2: Building domain model...")
print("=" * 60)
model = build_domain_model("doc", segments)
print(f"Extracted {len(model['classes'])} classes")
print(f"Extracted {len(model['relations'])} relations")

print("\nClasses:")
for cls in model['classes']:
    print(f"  - {cls['name']}: {len(cls['attributes'])} attributes")

print("\nRelations:")
for rel in model['relations']:
    print(f"  - {rel['source']} --{rel['label']}--> {rel['target']}")

print("\n" + "=" * 60)
print("STEP 3: Visualizing in Miro...")
print("=" * 60)
result = visualize_domain_model(BOARD_ID, model)
print(f"Created {result['summary']['classes_created']} class boxes")
print(f"Created {result['summary']['relations_created']} connectors")

print("\n✅ Done! Check your Miro board.")
