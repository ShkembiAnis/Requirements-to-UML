# app/miro_visualizer.py
from typing import Dict, List, Tuple
import math
from app.miro_client import create_class_box, get_headers, MIRO_API_BASE
import requests


def calculate_layout(num_classes: int, spacing: int = 400) -> List[Tuple[int, int]]:
    """
    Calculate grid layout positions for classes
    Returns list of (x, y) coordinates
    """
    if num_classes == 0:
        return []

    # Calculate grid dimensions
    cols = math.ceil(math.sqrt(num_classes))
    rows = math.ceil(num_classes / cols)

    positions = []
    for i in range(num_classes):
        row = i // cols
        col = i % cols

        # Center the grid around (0, 0)
        x = (col - cols / 2) * spacing
        y = (row - rows / 2) * spacing

        positions.append((int(x), int(y)))

    return positions


def create_connector(board_id: str, start_id: str, end_id: str, label: str = "", cardinality: dict = None):
    """
    Create a connector with multiplicities at both ends
    """
    url = f"{MIRO_API_BASE}/boards/{board_id}/connectors"

    payload = {
        "startItem": {"id": start_id},
        "endItem": {"id": end_id},
        "shape": "curved",
        "style": {
            "strokeColor": "#1A1A1A",
            "strokeWidth": 2,
            "endStrokeCap": "stealth"
        }
    }

    # Build captions list
    captions = []

    # Source multiplicity (near start)
    if cardinality and cardinality.get("source"):
        captions.append({
            "content": cardinality["source"],
            "position": "14%"  # Near source
        })

    # Relationship label (middle)
    if label:
        captions.append({
            "content": label,
            "position": "50%"  # Middle
        })

    # Target multiplicity (near end)
    if cardinality and cardinality.get("target"):
        captions.append({
            "content": cardinality["target"],
            "position": "86%"  # Near target
        })

    if captions:
        payload["captions"] = captions

    response = requests.post(url, json=payload, headers=get_headers())
    response.raise_for_status()
    return response.json()


def visualize_domain_model(board_id: str, domain_model: Dict) -> Dict:
    """
    Visualize the complete domain model in Miro
    Returns summary of created items
    """
    classes = domain_model.get("classes", [])
    relations = domain_model.get("relations", [])

    if not classes:
        return {"error": "No classes to visualize"}

    # Calculate positions
    positions = calculate_layout(len(classes))

    # Create class boxes and store their IDs
    class_id_map = {}  # class_name -> miro_shape_id
    created_boxes = []

    print(f"\nCreating {len(classes)} class boxes...")
    for i, cls in enumerate(classes):
        class_name = cls["name"]
        attributes = [attr["name"] for attr in cls.get("attributes", [])]
        x, y = positions[i]

        result = create_class_box(
            board_id=board_id,
            class_name=class_name,
            attributes=attributes,
            x=x,
            y=y
        )

        class_id_map[class_name] = result["id"]
        created_boxes.append({
            "class": class_name,
            "miro_id": result["id"],
            "position": {"x": x, "y": y}
        })
        print(f"  ✓ Created {class_name} with ID: {result['id']}")

    # Create connectors for relations
    created_connectors = []
    print(f"\nCreating {len(relations)} connectors...")
    for rel in relations:
        source_name = rel["source"]
        target_name = rel["target"]
        label = rel.get("label", "")
        cardinality = rel.get("cardinality", {"source": "1", "target": "0..*"})  # Get cardinality

        print(f"\nAttempting: {source_name} → {target_name}")

        # Check if both classes exist
        if source_name not in class_id_map:
            print(f"  ⚠️ Source class '{source_name}' not found in class_id_map")
            continue

        if target_name not in class_id_map:
            print(f"  ⚠️ Target class '{target_name}' not found in class_id_map")
            continue

        try:
            connector = create_connector(
                board_id=board_id,
                start_id=class_id_map[source_name],
                end_id=class_id_map[target_name],
                label=label,
                cardinality=cardinality  # Pass cardinality
            )
            created_connectors.append({
                "from": source_name,
                "to": target_name,
                "label": label,
                "cardinality": cardinality,
                "miro_id": connector["id"]
            })
            print(f"  ✓ Created connector: {source_name} [{cardinality['source']}] --{label}-> [{cardinality['target']}] {target_name}")
        except Exception as e:
            print(f"  ✗ Failed to create connector {source_name} → {target_name}")
            print(f"    Error: {e}")

    return {
        "board_id": board_id,
        "summary": {
            "classes_created": len(created_boxes),
            "relations_created": len(created_connectors)
        },
        "boxes": created_boxes,
        "connectors": created_connectors
    }
