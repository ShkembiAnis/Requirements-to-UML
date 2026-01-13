import os
import requests
from dotenv import load_dotenv

load_dotenv()

MIRO_API_BASE = "https://api.miro.com/v2"


def get_headers():
    token = os.getenv("MIRO_API_TOKEN")
    if not token:
        raise RuntimeError("MIRO_API_TOKEN not found in environment")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def estimate_height(num_lines: int) -> int:
    """Estimate height based on number of text lines"""
    base_padding = 50
    line_height = 20
    return base_padding + num_lines * line_height


def estimate_width(class_name: str, attributes: list, min_width: int = 220) -> int:
    """Estimate width based on longest text content"""
    # Find longest text (class name or attribute)
    longest = max([len(class_name)] + [len(a) for a in attributes] + [0])

    # Character width estimation (adjust multiplier based on font)
    char_width = 10  # pixels per character (approximate for fontSize 14)
    padding = 40    # left + right padding

    estimated = padding + longest * char_width

    # Clamp between min and max width
    return max(min_width, min(estimated, 600))


def divider_for_width(width_px: int) -> str:
    """Generate divider line that fits the box width"""
    # Use same char_width as estimate_width for consistency
    char_width = 10  # match the width estimation
    padding = 40  # total horizontal padding
    available_width = width_px - padding

    # Reduce by 20% to ensure it doesn't wrap
    num_chars = max(10, int((available_width / char_width) * 0.8))
    return "─" * num_chars


def create_class_box(board_id: str, class_name: str, attributes: list, x: int = 0, y: int = 0):
    """Create a UML class box using rectangle shape"""

    # Calculate dimensions
    width = estimate_width(class_name, attributes)
    num_lines = 2 + len(attributes)  # class name + divider + attributes
    height = estimate_height(num_lines)

    # Generate divider that matches the width
    divider = divider_for_width(width)

    # Build content with HTML
    content = f"<p><strong>{class_name}</strong></p><p>{divider}</p>"
    for attr in attributes:
        # Add "-" prefix if not already present
        if not attr.strip().startswith('-'):
            content += f"<p>- {attr}</p>"
        else:
            content += f"<p>{attr}</p>"

    url = f"{MIRO_API_BASE}/boards/{board_id}/shapes"

    payload = {
        "data": {
            "shape": "rectangle",
            "content": content
        },
        "style": {
            "fillColor": "#FFFFFF",
            "borderColor": "#1A1A1A",
            "borderWidth": 2,
            "fontSize": 14,
            "textAlign": "left",
            "textAlignVertical": "top"
        },
        "position": {
            "x": x,
            "y": y
        },
        "geometry": {
            "width": width,
            "height": height
        }
    }

    response = requests.post(url, json=payload, headers=get_headers())
    response.raise_for_status()
    return response.json()


def test_connection():
    """Sanity check: list boards"""
    url = f"{MIRO_API_BASE}/boards"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()
