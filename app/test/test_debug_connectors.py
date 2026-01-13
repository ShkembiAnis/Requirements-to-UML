# test_debug_connectors.py
from pathlib import Path
from app.filter import segment_text
from app.model_builder import build_domain_model
from app.miro_visualizer import visualize_domain_model

BOARD_ID = "uXjVGRZh1IE="

# Load sample requirements
sample_path = Path("data/input/sample_requirements.txt")
text = sample_path.read_text()

segments = segment_text(text)
model = build_domain_model("doc", segments)

print("=" * 60)
print("ATTEMPTING VISUALIZATION")
print("=" * 60)

try:
    result = visualize_domain_model(BOARD_ID, model)
    print("\n✅ Visualization completed!")
    print(f"Classes created: {result['summary']['classes_created']}")
    print(f"Relations created: {result['summary']['relations_created']}")

    print("\n📦 Boxes created:")
    for box in result['boxes']:
        print(f"  {box['class']}: ID={box['miro_id']}")

    print("\n🔗 Connectors created:")
    for conn in result['connectors']:
        print(f"  {conn['from']} → {conn['to']}: {conn['label']}")

    if len(result['connectors']) == 0:
        print("\n⚠️ No connectors were created!")
        print("Expected 2 connectors based on the domain model")

except Exception as e:
    print(f"\n❌ Error during visualization: {e}")
    import traceback
    traceback.print_exc()
