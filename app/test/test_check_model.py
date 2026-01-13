# test_check_model.py
from pathlib import Path
from app.filter import segment_text
from app.model_builder import build_domain_model
import json

# Load sample requirements
sample_path = Path("data/input/sample_requirements.txt")
text = sample_path.read_text()

segments = segment_text(text)
model = build_domain_model("doc", segments)

print("=" * 60)
print("EXTRACTED DOMAIN MODEL")
print("=" * 60)

print("\n📦 CLASSES:")
for cls in model['classes']:
    attrs = [a['name'] for a in cls.get('attributes', [])]
    print(f"  {cls['name']}: {attrs}")

print("\n🔗 RELATIONS:")
for rel in model['relations']:
    print(f"  {rel['source']} --[{rel['label']}]--> {rel['target']}")

print("\n" + "=" * 60)
print("Full model JSON:")
print("=" * 60)
print(json.dumps(model, indent=2))
