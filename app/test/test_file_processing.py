# app/tests/test_file_processing.py
from pathlib import Path
from app.file_processor import extract_text_from_file
from app.filter import segment_text
from app.model_builder import build_domain_model
from app.miro_visualizer import visualize_domain_model
import json


BOARD_ID = "uXjVGRZh1IE="  # Your Miro board ID


def test_file_type(file_path: str, create_miro: bool = False):
    """Test processing a single file"""
    print(f"\n{'='*60}")
    print(f"Testing: {file_path}")
    print(f"{'='*60}")

    try:
        # Extract text
        text = extract_text_from_file(file_path)
        print(f"\n📄 Extracted {len(text)} characters")
        print(f"\nFirst 500 characters:")
        print(text[:500])

        # Process
        segments = segment_text(text)
        model = build_domain_model("test", segments)

        # Show results
        print(f"\n📊 Results:")
        print(f"  Segments: {len(model['segments'])}")
        print(f"  Classes: {len(model['classes'])}")
        print(f"  Relations: {len(model['relations'])}")

        print(f"\n📦 Classes found:")
        for cls in model['classes']:
            attrs = [a['name'] for a in cls.get('attributes', [])]
            print(f"  - {cls['name']}: {attrs}")

        print(f"\n🔗 Relations found:")
        for rel in model['relations']:
            print(f"  - {rel['source']} --{rel['label']}--> {rel['target']}")

        # Create Miro diagram if requested
        if create_miro:
            print(f"\n{'='*60}")
            print("Creating Miro diagram...")
            print(f"{'='*60}")

            result = visualize_domain_model(BOARD_ID, model)

            print(f"\n✅ Miro Visualization Created!")
            print(f"Classes created: {result['summary']['classes_created']}")
            print(f"Relations created: {result['summary']['relations_created']}")
            print(f"\n🎨 View your diagram at: https://miro.com/app/board/{BOARD_ID}")

        return model

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


# Test with your files
if __name__ == "__main__":
    # Test PDF and create Miro diagram
    print("\n" + "="*60)
    print("TESTING PDF FILE")
    print("="*60)
    test_file_type("data/input/requirements.pdf", create_miro=True)

    # Optionally test TXT files too
    # test_file_type("data/input/sample_requirements.txt", create_miro=False)
